from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User, Project, DataContainer, DataItem, Annotation
from app.schemas import AnnotationCreate, AnnotationResponse
from app.auth import get_current_active_user

def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to check if current user is an admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="This endpoint requires admin privileges"
        )
    return current_user

router = APIRouter(tags=["admin-annotations"])

@router.post("/", response_model=AnnotationResponse)
def create_annotation(
    annotation: AnnotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Create a new annotation (admin only)"""
    # Verify item exists
    item = db.query(DataItem).filter(DataItem.id == annotation.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_annotation = Annotation(
        item_id=annotation.item_id,
        data=annotation.data,
        type=annotation.type,
        created_by_id=current_user.id
    )
    db.add(db_annotation)
    db.commit()
    db.refresh(db_annotation)
    return db_annotation

@router.get("/", response_model=List[AnnotationResponse])
def list_annotations(
    item_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """List all annotations (admin only)"""
    query = db.query(Annotation)
    if item_id:
        item = db.query(DataItem).filter(DataItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        query = query.filter(Annotation.item_id == item_id)
    return query.offset(skip).limit(limit).all()

@router.get("/{annotation_id}", response_model=AnnotationResponse)
def get_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Get annotation details (admin only)"""
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return annotation

@router.delete("/{annotation_id}", status_code=204)
def delete_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Delete an annotation (admin only)"""
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    db.delete(annotation)
    db.commit()
    return None 