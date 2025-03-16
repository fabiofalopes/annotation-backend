from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User, Project, DataContainer, DataItem
from app.schemas import DataItemCreate, DataItemResponse, DataItemWithAnnotations
from app.auth import get_current_active_user

def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to check if current user is an admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="This endpoint requires admin privileges"
        )
    return current_user

router = APIRouter(tags=["admin-items"])

@router.post("/", response_model=DataItemResponse)
def create_item(
    item: DataItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Create a new data item (admin only)"""
    # Verify container exists
    container = db.query(DataContainer).filter(DataContainer.id == item.container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    
    db_item = DataItem(
        content=item.content,
        container_id=item.container_id,
        sequence=item.sequence,
        item_metadata=item.item_metadata
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/", response_model=List[DataItemResponse])
def list_items(
    container_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """List all items (admin only)"""
    query = db.query(DataItem)
    if container_id:
        container = db.query(DataContainer).filter(DataContainer.id == container_id).first()
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
        query = query.filter(DataItem.container_id == container_id)
    return query.offset(skip).limit(limit).all()

@router.get("/{item_id}", response_model=DataItemWithAnnotations)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Get item details (admin only)"""
    item = db.query(DataItem).filter(DataItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Delete an item (admin only)"""
    item = db.query(DataItem).filter(DataItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return None 