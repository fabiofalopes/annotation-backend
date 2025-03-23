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

router = APIRouter(tags=["chat-disentanglement"])

# Track import progress in memory
import_progress: Dict[str, Dict] = {}

async def import_chat_room_internal(
    project_id: int,
    file_path: str,
    container_id: Optional[int],
    name: Optional[str],
    metadata_columns: Optional[Dict[str, str]],
    batch_size: int,
    db: Session,
    current_user: User,
    progress_callback: Optional[callable] = None
) -> DataContainer:
    """Internal function to handle chat room import logic"""
    # Create or get container
    container = None
    if container_id:
        container = db.query(DataContainer).filter(
            DataContainer.id == container_id,
            DataContainer.project_id == project_id
        ).first()
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
    else:
        container = DataContainer(
            name=name or f"Import {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            type="chat_rooms",
            project_id=project_id
        )
        db.add(container)
        db.commit()
        db.refresh(container)

    processed_rows = 0
    # Process the file in chunks
    for chunk in pd.read_csv(file_path, chunksize=batch_size):
        items_to_add = []
        for _, row in chunk.iterrows():
            # Map columns according to metadata_columns or use default names
            turn_id = str(row[metadata_columns.get('turn_id', 'turn_id')] if metadata_columns else row['turn_id'])
            user_id = str(row[metadata_columns.get('user_id', 'user_id')] if metadata_columns else row['user_id'])
            turn_text = str(row[metadata_columns.get('turn_text', 'turn_text')] if metadata_columns else row['turn_text'])
            reply_to = row[metadata_columns.get('reply_to_turn', 'reply_to_turn')] if metadata_columns else row.get('reply_to_turn')
            thread = row[metadata_columns.get('thread', 'thread')] if metadata_columns and 'thread' in metadata_columns else row.get('thread')

            item = DataItem(
                container_id=container.id,
                content=turn_text,
                item_type="chat_turn",
                item_metadata={
                    'turn_id': turn_id,
                    'user_id': user_id,
                    'reply_to_turn': str(reply_to) if pd.notna(reply_to) else None,
                    'thread': str(thread) if pd.notna(thread) else None
                }
            )
            items_to_add.append(item)

        # Bulk insert items
        db.bulk_save_objects(items_to_add)
        db.commit()

        processed_rows += len(chunk)
        if progress_callback:
            progress_callback(processed_rows)

    return container

async def process_import_in_background(
    import_id: str,
    project_id: int,
    file_path: str,
    container_id: Optional[int],
    name: Optional[str],
    metadata_columns: Optional[Dict[str, str]],
    batch_size: int,
    db: Session,
    current_user: User
):
    """Process import in background"""
    try:
        import_progress[import_id] = ImportProgress(
            id=import_id,
            status="processing",
            total_rows=0,
            processed_rows=0,
            errors=[],
            start_time=datetime.now()
        )

        # Get total rows first
        for chunk in pd.read_csv(file_path, chunksize=batch_size):
            import_progress[import_id].total_rows += len(chunk)

        # Process the file
        container = await import_chat_room_internal(
            project_id=project_id,
            file_path=file_path,
            container_id=container_id,
            name=name,
            metadata_columns=metadata_columns,
            batch_size=batch_size,
            db=db,
            current_user=current_user,
            progress_callback=lambda processed: update_import_progress(import_id, processed)
        )

        import_progress[import_id].status = "completed"
        import_progress[import_id].container_id = container.id
        import_progress[import_id].end_time = datetime.now()

    except Exception as e:
        import_progress[import_id].status = "failed"
        import_progress[import_id].errors.append(str(e))
        import_progress[import_id].end_time = datetime.now()
        raise

    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.unlink(file_path)

def update_import_progress(import_id: str, processed_rows: int):
    """Update import progress"""
    if import_id in import_progress:
        import_progress[import_id].processed_rows = processed_rows

@router.post("/projects/{project_id}/rooms/import", status_code=status.HTTP_202_ACCEPTED)
@router.post("/projects/{project_id}/containers/import", status_code=status.HTTP_202_ACCEPTED)
async def import_chat_room(
    background_tasks: BackgroundTasks,
    project_id: int,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    container_id: Optional[int] = Form(None),
    metadata_columns: Optional[str] = Form(None),
    batch_size: Optional[int] = Form(1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ImportStatus:
    """Import a chat room from a CSV file.
    
    The CSV should contain the following columns (or their mapped equivalents):
    - turn_id: Unique identifier for each turn
    - user_id: ID of the user who sent the message
    - turn_text: The message content
    - reply_to_turn: ID of the turn this message replies to
    - thread: Optional thread identifier
    
    The metadata_columns parameter can be used to specify custom mappings from 
    CSV column names to the standard field names.

    Returns an import ID that can be used to track progress.
    """
    try:
        # Verify project access and type
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.type == "chat_disentanglement"
        ).first()
        if not project or current_user not in project.users:
            raise HTTPException(status_code=404, detail="Project not found")

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            file_path = temp_file.name

        # Generate import ID
        import_id = f"import_{datetime.now().timestamp()}_{file.filename}"

        # Start background task
        background_tasks.add_task(
            process_import_in_background,
            import_id=import_id,
            project_id=project_id,
            file_path=file_path,
            container_id=container_id,
            name=name,
            metadata_columns=json.loads(metadata_columns) if metadata_columns else None,
            batch_size=batch_size,
            db=db,
            current_user=current_user
        )

        return ImportStatus(
            import_id=import_id,
            status="pending",
            message="Import started"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error starting import: {str(e)}"
        )

@router.get("/imports/{import_id}", response_model=ImportProgress)
async def get_import_progress(
    import_id: str,
    current_user: User = Depends(get_current_active_user)
) -> ImportProgress:
    """Get the progress of an import operation"""
    if import_id not in import_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import not found"
        )
    return import_progress[import_id]

@router.post("/projects/{project_id}/rooms/bulk-import", response_model=BulkImportResponse)
async def bulk_import_chat_rooms(
    project_id: int,
    files: List[UploadFile] = File(...),
    container_id: Optional[int] = Form(None),
    metadata_columns: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Bulk import multiple chat rooms from CSV files.
    """
    # Verify project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has access to the project
    if current_user not in project.users:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    if project.type != "chat_disentanglement":
        raise HTTPException(status_code=400, detail="Project is not a chat disentanglement project")

    # Parse metadata columns if provided
    try:
        metadata_mappings = json.loads(metadata_columns) if metadata_columns else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata_columns JSON")

    # Create or get container
    container = None
    if container_id:
        container = db.query(DataContainer).filter(
            DataContainer.id == container_id,
            DataContainer.project_id == project_id
        ).first()
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
    else:
        container = DataContainer(
            name=f"Bulk Import {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            type="chat_rooms",
            project_id=project_id
        )
        db.add(container)
        db.commit()
        db.refresh(container)

    # Initialize import operations
    import_ids = []
    
    for file in files:
        import_id = str(uuid.uuid4())
        import_ids.append(import_id)
        
        # Initialize in-memory progress tracking
        import_progress[import_id] = {
            "id": import_id,
            "status": "pending",
            "filename": file.filename,
            "total_rows": 0,
            "processed_rows": 0,
            "errors": [],
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "container_id": container.id,
            "metadata_columns": metadata_mappings.get(file.filename, {})
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Start background processing
            background_tasks.add_task(
                process_import_file,
                temp_file.name,
                import_id,
                project_id,
                container.id,
                metadata_mappings.get(file.filename, {}),
                db
            )
    
    return BulkImportResponse(
        message="Bulk import started",
        import_ids=import_ids,
        container_id=container.id
    )

async def process_import_file(
    file_path: str,
    import_id: str,
    project_id: int,
    container_id: int,
    metadata_columns: Dict[str, str],
    db: Session
):
    """
    Process a single file import in the background.
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        total_rows = len(df)
        
        # Update progress tracking
        import_progress[import_id]["total_rows"] = total_rows
        import_progress[import_id]["status"] = "processing"
        
        # Process in batches
        batch_size = 1000
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i + batch_size]
            
            try:
                # Create items from batch
                items_to_add = []
                for _, row in batch.iterrows():
                    item = DataItem(
                        container_id=container_id,
                        content=str(row[metadata_columns['turn_text']]),
                        item_type="chat_turn",
                        item_metadata={
                            'turn_id': str(row[metadata_columns['turn_id']]),
                            'user_id': str(row[metadata_columns['user_id']]),
                            'reply_to_turn': str(row[metadata_columns['reply_to_turn']]) if row[metadata_columns['reply_to_turn']] else None,
                            'thread': str(row[metadata_columns['thread']]) if 'thread' in metadata_columns and metadata_columns['thread'] else None
                        }
                    )
                    items_to_add.append(item)
                
                # Bulk insert
                db.bulk_save_objects(items_to_add)
                db.commit()
                
                # Update progress
                import_progress[import_id]["processed_rows"] = min(i + batch_size, total_rows)
                
                # Small delay to prevent database overload
                await asyncio.sleep(0.1)
                
            except Exception as e:
                import_progress[import_id]["errors"].append(f"Error in batch {i//batch_size}: {str(e)}")
        
        # Mark as completed
        import_progress[import_id]["status"] = "completed"
        import_progress[import_id]["end_time"] = datetime.now().isoformat()
        
    except Exception as e:
        # Update status on error
        import_progress[import_id]["status"] = "failed"
        import_progress[import_id]["errors"].append(str(e))
        import_progress[import_id]["end_time"] = datetime.now().isoformat()
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(file_path)
        except:
            pass

@router.get("/imports/{import_id}/progress", response_model=ImportProgress)
async def get_import_progress(
    import_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the progress of an import operation.
    """
    if import_id not in import_progress:
        raise HTTPException(status_code=404, detail="Import operation not found")
    
    progress = import_progress[import_id]
    
    # Convert datetime strings back to datetime objects
    start_time = datetime.fromisoformat(progress["start_time"])
    end_time = datetime.fromisoformat(progress["end_time"]) if progress["end_time"] else None
    
    return ImportProgress(
        id=progress["id"],
        status=progress["status"],
        filename=progress["filename"],
        total_rows=progress["total_rows"],
        processed_rows=progress["processed_rows"],
        errors=progress["errors"],
        start_time=start_time,
        end_time=end_time,
        container_id=progress["container_id"]
    )

@router.post("/imports/{import_id}/cancel")
async def cancel_import(
    import_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel an ongoing import operation.
    """
    if import_id not in import_progress:
        raise HTTPException(status_code=404, detail="Import operation not found")
    
    progress = import_progress[import_id]
    
    if progress["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed or failed import")
    
    progress["status"] = "cancelled"
    progress["end_time"] = datetime.now().isoformat()
    
    return {"message": "Import cancelled"}

@router.post("/imports/{import_id}/retry")
async def retry_import(
    import_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retry a failed import operation.
    """
    if import_id not in import_progress:
        raise HTTPException(status_code=404, detail="Import operation not found")
    
    progress = import_progress[import_id]
    
    if progress["status"] != "failed":
        raise HTTPException(status_code=400, detail="Can only retry failed imports")
    
    # Reset import status
    progress["status"] = "pending"
    progress["processed_rows"] = 0
    progress["errors"] = []
    progress["start_time"] = datetime.now().isoformat()
    progress["end_time"] = None
    
    # Start background processing
    background_tasks.add_task(
        process_import_file,
        progress["filename"],
        import_id,
        progress["container_id"],
        progress["metadata_columns"],
        db
    )
    
    return {"message": "Import retry started", "import_id": import_id}

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