from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.domains.annotations.schemas.schemas import BaseAnnotationCreate, BaseAnnotationResponse
from app.domains.annotations.services.annotation_service import AnnotationService
from app.domains.users.models.models import User
from app.api.dependencies.auth import get_current_user

router = APIRouter(tags=["annotations"])

@router.post("/data-items/{item_id}/annotations", response_model=BaseAnnotationResponse)
async def create_annotation(
    item_id: int,
    annotation: BaseAnnotationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new annotation for a data item.
    """
    return AnnotationService.create_annotation(db, item_id, annotation, current_user.id)

@router.get("/data-items/{item_id}/annotations", response_model=List[BaseAnnotationResponse])
async def get_annotations(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all annotations for a data item.
    """
    return AnnotationService.get_annotations_by_item(db, item_id)

@router.get("/annotations/{annotation_id}", response_model=BaseAnnotationResponse)
async def get_annotation(
    annotation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get an annotation by ID.
    """
    return AnnotationService.get_annotation(db, annotation_id)

@router.put("/annotations/{annotation_id}", response_model=BaseAnnotationResponse)
async def update_annotation(
    annotation_id: int,
    annotation_update: BaseAnnotationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an annotation.
    """
    return AnnotationService.update_annotation(db, annotation_id, annotation_update, current_user.id)

@router.delete("/annotations/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annotation(
    annotation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an annotation.
    """
    AnnotationService.delete_annotation(db, annotation_id)
    return None 