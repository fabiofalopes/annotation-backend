from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User, Project, DataContainer, DataItem
from app.schemas import DataItemCreate, DataItemResponse, DataItemWithAnnotations
from app.auth import get_current_active_user

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=List[DataItemResponse])
def list_items(
    container_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(DataItem)
    if container_id:
        container = db.query(DataContainer).filter(DataContainer.id == container_id).first()
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
        project = db.query(Project).filter(Project.id == container.project_id).first()
        if project.created_by_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not enough permissions")
        query = query.filter(DataItem.container_id == container_id)
    elif current_user.role != "admin":
        # Regular users can only see items from their projects
        query = query.join(DataContainer).join(Project).filter(Project.created_by_id == current_user.id)
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=DataItemResponse)
def create_item(
    item: DataItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify container access
    container = db.query(DataContainer).filter(DataContainer.id == item.container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    project = db.query(Project).filter(Project.id == container.project_id).first()
    if project.created_by_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_item = DataItem(
        content=item.content,
        container_id=item.container_id,
        sequence=item.sequence,
        created_by_id=current_user.id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/{item_id}", response_model=DataItemWithAnnotations)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    item = db.query(DataItem).filter(DataItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    container = db.query(DataContainer).filter(DataContainer.id == item.container_id).first()
    project = db.query(Project).filter(Project.id == container.project_id).first()
    if project.created_by_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return item 