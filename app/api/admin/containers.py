from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from typing import Dict, List, Optional, Any

from app.database import get_db
from app.models import User, Project, DataContainer, DataItem, Annotation
from app.schemas import (
    DataContainerCreate, 
    DataContainerResponse, 
    DataContainerWithItems,
    DataItemResponse,
    DataItemWithAnnotations,
    AnnotationResponse
)
from app.auth import get_current_active_user

def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to check if current user is an admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="This endpoint requires admin privileges"
        )
    return current_user

router = APIRouter(tags=["admin-containers"])

@router.post("/", response_model=DataContainerResponse)
def create_container(
    container: DataContainerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Create a new data container (admin only)"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == container.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_container = DataContainer(
        name=container.name,
        type=container.type,
        project_id=container.project_id,
        json_schema=container.json_schema
    )
    db.add(db_container)
    db.commit()
    db.refresh(db_container)
    return db_container

@router.get("/", response_model=List[DataContainerResponse])
def list_containers(
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """List all containers (admin only)"""
    query = db.query(DataContainer)
    if project_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        query = query.filter(DataContainer.project_id == project_id)
    return query.offset(skip).limit(limit).all()

@router.get("/{container_id}", response_model=DataContainerWithItems)
def get_container(
    container_id: int,
    include_items: bool = True,
    include_annotations: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Get container details (admin only)
    
    - include_items: Whether to include data items
    - include_annotations: Whether to include annotations for each data item
    """
    container = db.query(DataContainer).filter(DataContainer.id == container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    
    # Convert to response model
    result = DataContainerWithItems.model_validate(container)
    
    # Handle include_items and include_annotations
    if not include_items:
        result.items = []
    elif include_annotations and result.items:
        # We're already including the items and annotations via SQLAlchemy relationships
        # and Pydantic's model_validate, so no additional work needed
        pass
    
    return result 