from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User, Project, DataContainer
from app.schemas import DataContainerCreate, DataContainerResponse, DataContainerWithItems
from app.auth import get_current_active_user

router = APIRouter(prefix="/containers", tags=["containers"])

@router.post("/", response_model=DataContainerResponse)
def create_container(
    container: DataContainerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify project access
    project = db.query(Project).filter(Project.id == container.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user not in project.users and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
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
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(DataContainer)
    if project_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.created_by_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not enough permissions")
        query = query.filter(DataContainer.project_id == project_id)
    elif current_user.role != "admin":
        # Regular users can only see containers from their projects
        query = query.join(Project).filter(Project.created_by_id == current_user.id)
    return query.offset(skip).limit(limit).all()

@router.get("/{container_id}", response_model=DataContainerWithItems)
def get_container(
    container_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    container = db.query(DataContainer).filter(DataContainer.id == container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    project = db.query(Project).filter(Project.id == container.project_id).first()
    if project.created_by_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return container 