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

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_chat_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific chat disentanglement project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.type == "chat_disentanglement"
    ).first()
    if not project or current_user not in project.users:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/projects/{project_id}/rooms", response_model=List[DataContainerResponse])
async def list_chat_rooms(
    project_id: int,
    container_type: Optional[str] = None,
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
    
    # Base query
    query = db.query(DataContainer).filter(DataContainer.project_id == project_id)
    
    # Apply container type filter if specified
    if container_type:
        query = query.filter(DataContainer.type == container_type)
    
    return query.all()

@router.post("/projects/{project_id}/rooms/import", status_code=status.HTTP_201_CREATED)
@router.post("/projects/{project_id}/containers/import", status_code=status.HTTP_201_CREATED)
async def import_chat_room(
    project_id: int,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    container_id: Optional[int] = Form(None),
    metadata_columns: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Import a chat room from a CSV file.
    
    The CSV should contain the following columns (or their mapped equivalents):
    - turn_id: Unique identifier for each turn
    - user_id: ID of the user who sent the message
    - turn_text: The message content
    - reply_to_turn: ID of the turn this message replies to
    - thread: Optional thread identifier
    
    The metadata_columns parameter can be used to specify custom mappings from 
    CSV column names to the standard field names.
    """
    try:
        # Verify project access and type
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.type == "chat_disentanglement"
        ).first()
        if not project or current_user not in project.users:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get or create container
        if container_id:
            container = db.query(DataContainer).filter(
                DataContainer.id == container_id,
                DataContainer.project_id == project_id
            ).first()
            if not container or container.project_id != project_id:
                raise HTTPException(status_code=404, detail="Container not found")
            db_container = container
        else:
            # Create new container
            container_name = name or f"Chat Room from {file.filename}"
            db_container = DataContainer(
                name=container_name,
                type="chat_rooms",  # Fixed container type for chat rooms
                project_id=project.id,
                created_by_id=current_user.id,
                metadata={
                    "room_id": str(db.query(DataContainer).count() + 1),
                    "name": container_name,
                    "source_file": file.filename
                }
            )
            db.add(db_container)
            db.flush()

        # Read CSV content
        content = await file.read()
        df = pd.read_csv(StringIO(content.decode()))
        
        # Check if we have already mapped columns (from UI) or need to auto-detect
        column_mapping = {}
        use_direct_columns = False
        thread_column = "thread"
        
        if set(["turn_id", "user_id", "turn_text", "reply_to_turn"]).issubset(df.columns):
            # This is already a mapped CSV (from Streamlit UI)
            use_direct_columns = True
            required_fields = ["turn_id", "user_id", "turn_text", "reply_to_turn"]
            if "thread" in df.columns:
                thread_column = "thread"
        else:
            # Parse metadata columns if provided
            if metadata_columns:
                try:
                    # Parse the JSON metadata columns
                    parsed_mapping = json.loads(metadata_columns)
                    
                    # Check if it's a simple mapping or complex structure
                    if isinstance(parsed_mapping, dict):
                        # Extract column mappings
                        for field, col_name in parsed_mapping.items():
                            if field != "thread_id" and field in ["turn_id", "user_id", "turn_text", "reply_to_turn"]:
                                column_mapping[field] = col_name
                            elif field == "thread_id" or field == "thread":
                                thread_column = col_name
                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid metadata_columns format. Expected JSON object."
                    )
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Error processing metadata_columns: {str(e)}"
                    )
            
            # If no column mapping was provided or it's incomplete, try auto-detection
            required_fields = ["turn_id", "user_id", "turn_text", "reply_to_turn"]
            
            # Use auto-detection for any missing fields
            for field in required_fields:
                if field not in column_mapping:
                    # Try exact match first
                    if field in df.columns:
                        column_mapping[field] = field
                    else:
                        # Try common variations based on field
                        variations = []
                        if field == "turn_id":
                            variations = ["turn id", "turnid", "turn", "message_id", "msg_id", "id"]
                        elif field == "user_id":
                            variations = ["user id", "userid", "user", "speaker", "speaker_id", "author"]
                        elif field == "turn_text":
                            variations = ["text", "content", "message", "turn_content", "msg_text", "message_text"]
                        elif field == "reply_to_turn":
                            variations = ["reply_to", "replyto", "in_reply_to", "parent_id", "reply"]
                        
                        # Check for variations
                        for col in df.columns:
                            if col.lower() in [v.lower() for v in variations]:
                                column_mapping[field] = col
                                break
            
            # Verify all required fields are mapped
            missing_fields = [field for field in required_fields if field not in column_mapping]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required column mappings: {', '.join(missing_fields)}. Available columns: {', '.join(df.columns)}"
                )
            
            # Try to find thread column if not specified
            if not thread_column:
                for col in df.columns:
                    if "thread" in col.lower():
                        thread_column = col
                        break
        
        # Process rows
        for idx, row in df.iterrows():
            # Create data item with appropriate mapping method
            if use_direct_columns:
                # If columns are already mapped in the CSV (from UI)
                item_metadata = {
                    'turn_id': str(row['turn_id']),
                    'user_id': str(row['user_id']),
                    'reply_to': str(row['reply_to_turn']) if pd.notna(row['reply_to_turn']) else None
                }
                
                # Add thread_id to metadata if present in CSV
                if thread_column in df.columns and pd.notna(row[thread_column]):
                    item_metadata['thread_id'] = str(row[thread_column])
                
                content = str(row['turn_text'])
            else:
                # If using source column mapping
                item_metadata = {
                    'turn_id': str(row[column_mapping['turn_id']]),
                    'user_id': str(row[column_mapping['user_id']]),
                    'reply_to': str(row[column_mapping['reply_to_turn']]) if pd.notna(row[column_mapping['reply_to_turn']]) else None
                }
                
                # Add thread_id to metadata if present in CSV
                if thread_column and thread_column in df.columns and pd.notna(row[thread_column]):
                    item_metadata['thread_id'] = str(row[thread_column])
                
                content = str(row[column_mapping['turn_text']])
            
            item = DataItem(
                container_id=db_container.id,
                content=content,
                item_metadata=item_metadata,
                sequence=idx
            )
            db.add(item)
            db.flush()  # Get item ID without committing

            # Create thread annotation if thread column exists
            if thread_column and thread_column in df.columns and pd.notna(row[thread_column]):
                annotation = Annotation(
                    item_id=item.id,
                    created_by_id=current_user.id,
                    type="thread",
                    data={
                        "thread_id": str(row[thread_column]),
                        "source": "imported",
                        "import_timestamp": str(pd.Timestamp.now()),
                        "original_column": thread_column
                    }
                )
                db.add(annotation)

        # Commit all changes
        db.commit()
        
        # Prepare detailed response
        response_data = {
            "message": "Chat room imported successfully",
            "container_id": db_container.id,
            "items_imported": len(df),
            "column_mapping": column_mapping if not use_direct_columns else "direct",
            "direct_columns_used": use_direct_columns,
            "mapped_columns": {
                "turn_id": column_mapping.get("turn_id") if not use_direct_columns else "turn_id",
                "user_id": column_mapping.get("user_id") if not use_direct_columns else "user_id",
                "turn_text": column_mapping.get("turn_text") if not use_direct_columns else "turn_text",
                "reply_to_turn": column_mapping.get("reply_to_turn") if not use_direct_columns else "reply_to_turn",
                "thread": thread_column
            },
            "available_columns": list(df.columns)
        }
        
        return response_data

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error importing data: {str(e)}"
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
        DataContainer.type == "chat_rooms"
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
        DataContainer.type == "chat_rooms"
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
        DataContainer.type == "chat_rooms"
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

@router.get("/debug/info")
async def get_debug_info(
    current_user: User = Depends(get_current_active_user)
):
    """Debug endpoint to check API connectivity"""
    return {
        "username": current_user.username,
        "routes": [
            {"path": "/projects", "method": "GET", "description": "List projects"},
            {"path": "/projects/{project_id}/rooms", "method": "GET", "description": "List rooms in project"},
            {"path": "/projects/{project_id}/rooms/import", "method": "POST", "description": "Import chat room data"},
            {"path": "/projects/{project_id}/containers/import", "method": "POST", "description": "Alternative import endpoint"}
        ],
        "message": "If you can see this, the API connection is working"
    } 

@router.get("/debug/routes")
async def list_routes():
    """List all routes registered in this router for debugging"""
    routes = []
    for route in router.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods),
            "endpoint": route.endpoint.__name__ if hasattr(route.endpoint, "__name__") else str(route.endpoint)
        })
    return {"routes": routes} 