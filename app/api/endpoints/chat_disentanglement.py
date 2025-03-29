from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Type, Any
import pandas as pd
from io import StringIO
import json
from sqlalchemy import inspect
from sqlalchemy.orm import class_mapper
from pydantic import BaseModel
import inspect as python_inspect
import tempfile
import os
import asyncio
from datetime import datetime
import uuid
import time

from app.database import get_db, engine
from app.models import User, Project, DataContainer, DataItem, Annotation
from app.auth import get_current_active_user
from app.schemas import (
    ChatRoomImport, ChatRoomSchema, ChatTurn,
    ProjectResponse, DataContainerResponse,
    ProjectCreate, DataContainerCreate, DataItemCreate, AnnotationCreate,
    ProjectWithContainers, DataContainerWithItems, DataItemWithAnnotations,
    ImportStatus, BulkImportResponse, ImportProgress
)
from app.services.import_service import ImportService
from app.services.progress_service import ProgressService
from app.services.file_service import FileService
from app.config import settings

router = APIRouter(tags=["chat-disentanglement"])

async def process_import_in_background(
    import_id: str,
    project_id: int,
    file: UploadFile,
    container_id: Optional[int],
    name: Optional[str],
    metadata_columns: Optional[Dict[str, str]],
    batch_size: int,
    db: Session,
    current_user: User
):
    """Process import in background"""
    try:
        # Initialize services
        import_service = ImportService(db, current_user)
        progress_service = ProgressService(db)

        # Save uploaded file temporarily
        file_path = await import_service.save_upload_file(file)

        try:
            # Get total rows first
            total_rows = import_service.count_rows(file_path)
            progress_service.update_progress(import_id, 0, total_rows=total_rows, status="processing")

            # Process the file
            container = await import_service.import_data(
                project_id=project_id,
                file_path=file_path,
                container_id=container_id,
                name=name,
                metadata_columns=metadata_columns,
                batch_size=batch_size,
                progress_callback=lambda processed, total, **kwargs: progress_service.update_progress(
                    import_id, processed, total_rows=total, status="processing", **kwargs
                )
            )

            # Update progress with container ID and completion status
            progress_service.update_progress(
                import_id, 
                total_rows, 
                total_rows=total_rows, 
                status="completed",
                container_id=container.id
            )

        finally:
            # Clean up temporary file
            import_service.cleanup_file(file_path)

    except Exception as e:
        # Update progress with error status
        progress_service.update_progress(
            import_id, 
            0,  # processed_rows
            status="failed", 
            error=str(e)
        )
        raise

@router.post("/projects/{project_id}/rooms/import", response_model=Dict[str, Any])
async def import_chat_room(
    project_id: int,
    file: UploadFile = File(...),
    name: str = Form(...),
    metadata_columns: Optional[str] = Form(None),
    container_id: Optional[int] = Form(None),
    batch_size: int = Form(settings.DEFAULT_BATCH_SIZE),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Import a chat room from a CSV file."""
    progress_service = ProgressService(db)
    progress_record = None
    progress_id = f"import_{time.time()}_{file.filename}"

    try:
        # Parse metadata_columns if provided
        parsed_metadata = None
        if metadata_columns:
            try:
                parsed_metadata = json.loads(metadata_columns)
                if not isinstance(parsed_metadata, dict):
                    raise ValueError("metadata_columns must be a JSON object")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid metadata_columns JSON: {str(e)}")

        # Create progress record
        progress_record = progress_service.create_progress(
            import_id=progress_id,
            filename=file.filename,
            container_id=container_id,
            metadata_columns=parsed_metadata
        )

        # Process import in background
        asyncio.create_task(process_import_in_background(
            import_id=progress_id,
            project_id=project_id,
            file=file,
            name=name,
            metadata_columns=parsed_metadata,
            container_id=container_id,
            batch_size=batch_size,
            db=db,
            current_user=current_user
        ))

        return {
            "message": "Import started",
            "import_id": progress_id
        }

    except ValueError as e:
        # Handle validation errors
        if progress_record:
            progress_service.update_progress(
                import_id=progress_id,
                processed_rows=0,
                status="failed",
                error=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Handle other errors
        if progress_record:
            progress_service.update_progress(
                import_id=progress_id,
                processed_rows=0,
                status="failed",
                error=f"Import failed: {str(e)}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )

@router.get("/imports/{import_id}", response_model=ImportProgress)
async def get_import_progress(
    import_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ImportProgress:
    """Get the progress of an import operation"""
    progress_service = ProgressService(db)
    try:
        return progress_service.get_progress(import_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/imports/{import_id}/cancel")
async def cancel_import(
    import_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel an ongoing import operation."""
    progress_service = ProgressService(db)
    try:
        progress_service.cancel_progress(import_id)
        return {"message": "Import cancelled"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/imports/{import_id}/retry")
async def retry_import(
    import_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retry a failed import operation."""
    progress_service = ProgressService(db)
    try:
        progress = progress_service.retry_progress(import_id)
        return {"message": "Import retry started", "import_id": import_id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

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
    """Get the database schema information for chat disentanglement models."""
    inspector = inspect(engine)
    schema_info = {}
    
    # List of models we want to include in the schema
    models = {
        'projects': 'project',
        'data_containers': 'data_container',
        'data_items': 'data_item',
        'annotations': 'annotation',
        'import_progress': 'import_progress'
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
    """Get the schema information directly from the code."""
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
                'uselist': rel.uselist
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
    models = [Project, DataContainer, DataItem, Annotation, ImportProgress]
    for model in models:
        schema_info['sqlalchemy_models'][model.__name__] = get_sqlalchemy_model_info(model)
    
    # Pydantic schemas
    schemas = [
        ProjectCreate, ProjectResponse, ProjectWithContainers,
        DataContainerCreate, DataContainerResponse, DataContainerWithItems,
        DataItemCreate, DataItemWithAnnotations,
        ChatRoomSchema, ChatTurn, ImportProgress
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

@router.post("/validate-csv", response_model=Dict[str, Any])
async def validate_csv(
    file: UploadFile = File(...),
    metadata_columns: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Validate a CSV file before import."""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            file_path = temp_file.name

        try:
            # Read first row to check columns
            df = pd.read_csv(file_path, nrows=1)
            
            # Get column mapping
            column_mapping = {
                'turn_id': 'turn_id',
                'user_id': 'user_id',
                'turn_text': 'turn_text',
                'reply_to_turn': 'reply_to_turn',
                'thread': 'thread'
            }
            
            if metadata_columns:
                custom_mapping = json.loads(metadata_columns)
                column_mapping.update(custom_mapping)
            
            # Validate required columns exist
            missing_columns = [
                col for col in column_mapping.values()
                if col not in df.columns
            ]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Check if file is empty
            if df.empty:
                raise ValueError("File is empty")
            
            # Get total rows
            total_rows = sum(1 for _ in pd.read_csv(file_path, chunksize=1000))
            
            return {
                "valid": True,
                "total_rows": total_rows,
                "columns": list(df.columns),
                "column_mapping": column_mapping
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.unlink(file_path)
                
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 