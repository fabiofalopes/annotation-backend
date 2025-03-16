from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User, Project, DataContainer, DataItem, Annotation
from app.schemas import AnnotationCreate, AnnotationResponse
from app.auth import get_current_active_user

router = APIRouter(prefix="/annotations", tags=["annotations"])

@router.post("/", response_model=AnnotationResponse)
def create_annotation(
    annotation: AnnotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify item access
    item = db.query(DataItem).filter(DataItem.id == annotation.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    container = db.query(DataContainer).filter(DataContainer.id == item.container_id).first()
    project = db.query(Project).filter(Project.id == container.project_id).first()
    if project.created_by_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_annotation = Annotation(
        item_id=annotation.item_id,
        data=annotation.data,
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
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Annotation)
    if item_id:
        item = db.query(DataItem).filter(DataItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        container = db.query(DataContainer).filter(DataContainer.id == item.container_id).first()
        project = db.query(Project).filter(Project.id == container.project_id).first()
        if project.created_by_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not enough permissions")
        query = query.filter(Annotation.item_id == item_id)
    elif current_user.role != "admin":
        # Regular users can only see annotations from their projects
        query = query.join(DataItem).join(DataContainer).join(Project).filter(Project.created_by_id == current_user.id)
    return query.offset(skip).limit(limit).all()

@router.get("/{annotation_id}", response_model=AnnotationResponse)
def get_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    item = db.query(DataItem).filter(DataItem.id == annotation.item_id).first()
    container = db.query(DataContainer).filter(DataContainer.id == item.container_id).first()
    project = db.query(Project).filter(Project.id == container.project_id).first()
    if project.created_by_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return annotation 