from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.domains.annotations.models.models import BaseAnnotation
from app.domains.annotations.schemas.schemas import BaseAnnotationCreate
from app.domains.datasets.models.models import DataItem
from app.domains.annotations.exceptions.exceptions import AnnotationNotFoundError, InvalidAnnotationPositionError

class AnnotationService:
    @staticmethod
    def create_annotation(
        db: Session, 
        item_id: int, 
        annotation: BaseAnnotationCreate, 
        user_id: int
    ) -> BaseAnnotation:
        """
        Create a new annotation for a data item.
        """
        # Check if data item exists
        data_item = db.query(DataItem).filter(DataItem.id == item_id).first()
        if not data_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data item with ID {item_id} not found"
            )
        
        # Validate start_addr and end_addr if provided
        if annotation.start_addr is not None and annotation.end_addr is not None:
            if annotation.start_addr < 0 or annotation.end_addr > len(data_item.content) or annotation.start_addr >= annotation.end_addr:
                raise InvalidAnnotationPositionError()
        
        # Create new annotation
        db_annotation = BaseAnnotation(
            item_id=item_id,
            start_addr=annotation.start_addr,
            end_addr=annotation.end_addr,
            annotation_data=annotation.annotation_data,
            created_by=user_id,
            source=annotation.source,
            annotation_type_id=annotation.annotation_type_id
        )
        
        db.add(db_annotation)
        db.commit()
        db.refresh(db_annotation)
        
        return db_annotation
    
    @staticmethod
    def get_annotation(db: Session, annotation_id: int) -> BaseAnnotation:
        """
        Get an annotation by ID.
        """
        annotation = db.query(BaseAnnotation).filter(BaseAnnotation.id == annotation_id).first()
        
        if not annotation:
            raise AnnotationNotFoundError(annotation_id)
        
        return annotation
    
    @staticmethod
    def get_annotations_by_item(db: Session, item_id: int) -> List[BaseAnnotation]:
        """
        Get all annotations for a data item.
        """
        # Check if data item exists
        data_item = db.query(DataItem).filter(DataItem.id == item_id).first()
        if not data_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data item with ID {item_id} not found"
            )
        
        # Get annotations
        annotations = db.query(BaseAnnotation).filter(BaseAnnotation.item_id == item_id).all()
        
        return annotations
    
    @staticmethod
    def update_annotation(
        db: Session, 
        annotation_id: int, 
        annotation_update: BaseAnnotationCreate, 
        user_id: int
    ) -> BaseAnnotation:
        """
        Update an annotation.
        """
        # Get annotation
        db_annotation = db.query(BaseAnnotation).filter(BaseAnnotation.id == annotation_id).first()
        
        if not db_annotation:
            raise AnnotationNotFoundError(annotation_id)
        
        # Get data item to validate positions
        data_item = db.query(DataItem).filter(DataItem.id == db_annotation.item_id).first()
        
        # Validate start_addr and end_addr if provided
        if annotation_update.start_addr is not None and annotation_update.end_addr is not None:
            if annotation_update.start_addr < 0 or annotation_update.end_addr > len(data_item.content) or annotation_update.start_addr >= annotation_update.end_addr:
                raise InvalidAnnotationPositionError()
        
        # Update annotation
        db_annotation.start_addr = annotation_update.start_addr
        db_annotation.end_addr = annotation_update.end_addr
        db_annotation.annotation_data = annotation_update.annotation_data
        db_annotation.annotation_type_id = annotation_update.annotation_type_id
        
        db.commit()
        db.refresh(db_annotation)
        
        return db_annotation
    
    @staticmethod
    def delete_annotation(db: Session, annotation_id: int) -> None:
        """
        Delete an annotation.
        """
        # Get annotation
        db_annotation = db.query(BaseAnnotation).filter(BaseAnnotation.id == annotation_id).first()
        
        if not db_annotation:
            raise AnnotationNotFoundError(annotation_id)
        
        # Delete annotation
        db.delete(db_annotation)
        db.commit() 