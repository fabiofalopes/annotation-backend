from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Type
import pandas as pd
from io import StringIO
import json
from sqlalchemy import inspect
from sqlalchemy.orm import class_mapper
from pydantic import BaseModel
import inspect as python_inspect

from app.database import get_db, engine
from app.models import User, Project, DataContainer, DataItem, Annotation
from app.auth import get_current_active_user
from app.schemas import (
    ChatRoomImport, ChatRoomSchema, ChatTurn,
    ProjectResponse, DataContainerResponse,
    ProjectCreate, DataContainerCreate, DataItemCreate, AnnotationCreate,
    ProjectWithContainers, DataContainerWithItems, DataItemWithAnnotations
)

router = APIRouter(tags=["chat-disentanglement"])

# Project-related endpoints
@router.get("/projects", response_model=List[ProjectResponse])
async def list_chat_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all chat disentanglement projects accessible to the user"""
    return [
        project for project in current_user.projects 
        if project.type == "chat_disentanglement"
    ]

@router.get("/projects/{project_id}/rooms", response_model=List[DataContainerResponse])
async def list_chat_rooms(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all chat rooms in a project"""
    # Verify project access and type
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.type == "chat_disentanglement"
    ).first()
    if not project or current_user not in project.users:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return db.query(DataContainer).filter(
        DataContainer.project_id == project_id,
        DataContainer.type == "chat_room"
    ).all()

@router.post("/projects/{project_id}/rooms/import", status_code=status.HTTP_201_CREATED)
async def import_chat_room(
    project_id: int,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Import a chat room from a CSV file.
    
    Expected CSV format:
    turn_id,user_id,content,reply_to,thread
    1,user1,"Hello!",null,thread1
    2,user2,"Hi there!",1,thread1
    """
    try:
        # Verify project access and type
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.type == "chat_disentanglement"
        ).first()
        if not project or current_user not in project.users:
            raise HTTPException(status_code=404, detail="Project not found")

        # Read CSV content
        content = await file.read()
        df = pd.read_csv(StringIO(content.decode()))
        
        # Map columns from VAC_R10.csv format to expected format
        column_mapping = {
            'turn_text': 'content',
            'reply_to_turn': 'reply_to'
        }
        df = df.rename(columns=column_mapping)
        
        # Verify required columns (strict checking for these)
        required_columns = ['turn_id', 'user_id', 'content', 'reply_to']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV must contain columns: {', '.join(required_columns)}"
            )

        # Find thread column - look for any column containing 'thread' (case insensitive)
        thread_column = None
        for col in df.columns:
            if 'thread' in col.lower():
                thread_column = col
                break

        # Create container
        container_name = f"Chat Room {name or file.filename}"
        db_container = DataContainer(
            name=container_name,
            type="chat_room",
            project_id=project.id,
            json_schema={
                "type": "object",
                "properties": {
                    "room_id": {"type": "string"},
                    "name": {"type": "string"},
                    "messages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "turn_id": {"type": "string"},
                                "user_id": {"type": "string"},
                                "content": {"type": "string"},
                                "reply_to": {"type": "string", "nullable": True},
                                "thread": {"type": "string", "nullable": True}
                            },
                            "required": ["turn_id", "user_id", "content"]
                        }
                    }
                },
                "required": ["room_id", "name", "messages"]
            },
            created_by_id=current_user.id,
            metadata={
                "room_id": str(db.query(DataContainer).count() + 1),
                "name": container_name
            }
        )
        db.add(db_container)
        db.flush()  # Get container ID without committing

        # Process rows
        for _, row in df.iterrows():
            # Create data item
            item = DataItem(
                container_id=db_container.id,
                content=str(row['content']),
                item_metadata={
                    'turn_id': str(row['turn_id']),
                    'user_id': str(row['user_id']),
                    'reply_to': str(row['reply_to']) if pd.notna(row['reply_to']) else None
                },
                sequence=_  # Use DataFrame index as sequence
            )
            db.add(item)
            db.flush()  # Get item ID without committing

            # If thread column exists and has a value, create an annotation
            if thread_column and pd.notna(row[thread_column]):
                annotation = Annotation(
                    item_id=item.id,
                    created_by_id=current_user.id,
                    type="thread",
                    data={
                        "thread_id": str(row[thread_column]),
                        "source": "imported",
                        "import_timestamp": str(pd.Timestamp.now()),
                        "original_column_name": thread_column  # Store original column name for reference
                    }
                )
                db.add(annotation)

        db.commit()
        return {
            "message": "Chat room imported successfully",
            "container_id": db_container.id,
            "thread_column_used": thread_column
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/rooms/{room_id}/turns", response_model=List[ChatTurn])
async def list_chat_turns(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all turns in a chat room, ordered by sequence"""
    # Verify container access and type
    container = db.query(DataContainer).filter(
        DataContainer.id == room_id,
        DataContainer.type == "chat_room"
    ).first()
    if not container or current_user not in container.project.users:
        raise HTTPException(status_code=404, detail="Chat room not found")

    # Get turns
    items = db.query(DataItem).filter(
        DataItem.container_id == room_id
    ).order_by(DataItem.sequence).all()

    # Convert to ChatTurn models
    turns = []
    for item in items:
        metadata = item.item_metadata or {}
        turn = ChatTurn(
            turn_id=metadata.get('turn_id', str(item.id)),
            user_id=metadata.get('user_id', ''),
            content=item.content,
            reply_to=metadata.get('reply_to'),
            timestamp=None  # We don't have timestamps in our data
        )
        turns.append(turn)

    return turns

@router.get("/rooms/{room_id}/threads")
async def list_threads(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all threads in a chat room"""
    # Verify container access and type
    container = db.query(DataContainer).filter(
        DataContainer.id == room_id,
        DataContainer.type == "chat_room"
    ).first()
    if not container or current_user not in container.project.users:
        raise HTTPException(status_code=404, detail="Chat room not found")

    # Get all thread annotations for this room
    annotations = (
        db.query(Annotation)
        .join(DataItem)
        .filter(
            DataItem.container_id == room_id,
            Annotation.type == "thread"
        )
        .order_by(DataItem.sequence)
        .all()
    )

    # Group turns by thread
    threads = {}
    for annotation in annotations:
        thread_id = annotation.data.get("thread_id")
        if thread_id:
            if thread_id not in threads:
                threads[thread_id] = {
                    "thread_id": thread_id,
                    "source": annotation.data.get("source", "created"),
                    "turns": []
                }
            threads[thread_id]["turns"].append({
                "turn_id": annotation.item.item_metadata.get("turn_id"),
                "content": annotation.item.content,
                "user_id": annotation.item.item_metadata.get("user_id"),
                "sequence": annotation.item.sequence
            })

    return list(threads.values())

@router.post("/rooms/{room_id}/turns/{turn_id}/thread")
async def annotate_thread(
    room_id: int,
    turn_id: str,
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Annotate a turn as belonging to a thread"""
    # Verify container access and type
    container = db.query(DataContainer).filter(
        DataContainer.id == room_id,
        DataContainer.type == "chat_room"
    ).first()
    if not container or current_user not in container.project.users:
        raise HTTPException(status_code=404, detail="Chat room not found")

    # Find the turn
    item = db.query(DataItem).filter(
        DataItem.container_id == room_id,
        DataItem.item_metadata["turn_id"].astext == turn_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Turn not found")

    # Create or update thread annotation
    annotation = db.query(Annotation).filter(
        Annotation.item_id == item.id,
        Annotation.type == "thread"
    ).first()

    if annotation:
        # Update existing annotation
        annotation.data = {
            "thread_id": thread_id,
            "source": "created",
            "updated_at": str(pd.Timestamp.now())
        }
    else:
        # Create new annotation
        annotation = Annotation(
            item_id=item.id,
            created_by_id=current_user.id,
            type="thread",
            data={
                "thread_id": thread_id,
                "source": "created",
                "created_at": str(pd.Timestamp.now())
            }
        )
        db.add(annotation)

    db.commit()
    return {"message": "Thread annotation updated successfully"}

@router.get("/schema", response_model=Dict[str, Dict])
async def get_schema(
    current_user: User = Depends(get_current_active_user)
):
    """Get the database schema information for chat disentanglement models.
    This endpoint returns detailed information about the tables and their relationships.
    """
    inspector = inspect(engine)
    schema_info = {}
    
    # List of models we want to include in the schema
    models = {
        'projects': 'project',
        'data_containers': 'data_container',
        'data_items': 'data_item',
        'annotations': 'annotation'
    }
    
    for table_name, model_name in models.items():
        table_info = {
            'columns': {},
            'relationships': [],
            'foreign_keys': [],
            'indices': []
        }
        
        # Get column information
        for column in inspector.get_columns(table_name):
            table_info['columns'][column['name']] = {
                'type': str(column['type']),
                'nullable': column.get('nullable', True),
                'default': str(column.get('default', None)),
                'primary_key': column.get('primary_key', False)
            }
        
        # Get foreign key information
        for fk in inspector.get_foreign_keys(table_name):
            table_info['foreign_keys'].append({
                'constrained_columns': fk['constrained_columns'],
                'referred_table': fk['referred_table'],
                'referred_columns': fk['referred_columns']
            })
        
        # Get index information
        for idx in inspector.get_indexes(table_name):
            table_info['indices'].append({
                'name': idx['name'],
                'columns': idx['column_names'],
                'unique': idx['unique']
            })
        
        schema_info[model_name] = table_info
    
    return schema_info 

@router.get("/code-schema", response_model=Dict[str, Dict])
async def get_code_schema(
    current_user: User = Depends(get_current_active_user)
):
    """Get the schema information directly from the code (models and schemas).
    This endpoint analyzes the SQLAlchemy models and Pydantic schemas to provide
    a complete picture of the data model as defined in the code.
    """
    def get_sqlalchemy_model_info(model: Type) -> dict:
        """Extract information from a SQLAlchemy model"""
        mapper = class_mapper(model)
        info = {
            'type': 'sqlalchemy_model',
            'table_name': mapper.local_table.name,
            'columns': {},
            'relationships': [],
            'inheritance': []
        }
        
        # Get columns
        for column in mapper.columns:
            info['columns'][column.name] = {
                'type': str(column.type),
                'nullable': column.nullable,
                'primary_key': column.primary_key,
                'foreign_key': bool(column.foreign_keys),
                'default': str(column.default) if column.default else None
            }
        
        # Get relationships
        for rel in mapper.relationships:
            info['relationships'].append({
                'name': rel.key,
                'target': rel.target.name,
                'type': str(rel.direction.name),
                'uselist': rel.uselist  # True for one-to-many/many-to-many
            })
        
        # Get inheritance info
        for base in model.__bases__:
            if hasattr(base, '__table__'):
                info['inheritance'].append(base.__name__)
        
        return info

    def get_pydantic_model_info(model: Type[BaseModel]) -> dict:
        """Extract information from a Pydantic model"""
        info = {
            'type': 'pydantic_model',
            'fields': {},
            'config': {},
            'inheritance': []
        }
        
        # Get fields
        for name, field in model.model_fields.items():
            field_info = {
                'type': str(field.annotation),
                'required': field.is_required(),
                'default': str(field.default) if field.default else None,
                'description': field.description
            }
            info['fields'][name] = field_info
        
        # Get inheritance info
        for base in model.__bases__:
            if issubclass(base, BaseModel) and base != BaseModel:
                info['inheritance'].append(base.__name__)
        
        # Get config
        if hasattr(model, 'model_config'):
            info['config'] = {
                key: value for key, value in model.model_config.items()
                if not key.startswith('_')
            }
        
        return info

    schema_info = {
        'sqlalchemy_models': {},
        'pydantic_schemas': {}
    }
    
    # SQLAlchemy models
    models = [Project, DataContainer, DataItem, Annotation]
    for model in models:
        schema_info['sqlalchemy_models'][model.__name__] = get_sqlalchemy_model_info(model)
    
    # Pydantic schemas
    schemas = [
        ProjectCreate, ProjectResponse, ProjectWithContainers,
        DataContainerCreate, DataContainerResponse, DataContainerWithItems,
        DataItemCreate, DataItemWithAnnotations,
        ChatRoomSchema, ChatTurn
    ]
    for schema in schemas:
        schema_info['pydantic_schemas'][schema.__name__] = get_pydantic_model_info(schema)
    
    # Add relationships between models and schemas
    schema_info['model_schema_mappings'] = {
        'Project': {
            'create': 'ProjectCreate',
            'response': 'ProjectResponse',
            'detailed': 'ProjectWithContainers'
        },
        'DataContainer': {
            'create': 'DataContainerCreate',
            'response': 'DataContainerResponse',
            'detailed': 'DataContainerWithItems'
        },
        'DataItem': {
            'create': 'DataItemCreate',
            'detailed': 'DataItemWithAnnotations'
        }
    }
    
    return schema_info 