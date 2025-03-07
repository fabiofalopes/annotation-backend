"""
Script to create annotation types in the database.
"""
from app.infrastructure.database import SessionLocal
from app.domains.annotations.models.models import AnnotationType
import json

def create_annotation_type():
    db = SessionLocal()
    try:
        # Define the schema for thread disentanglement annotations
        schema = {
            "type": "object",
            "properties": {
                "threads": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string"},
                            "message_ids": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["thread_id", "message_ids"]
                    }
                }
            },
            "required": ["threads"]
        }
        
        # Check if the annotation type already exists
        existing = db.query(AnnotationType).filter(AnnotationType.name == "thread_disentanglement").first()
        if existing:
            print(f"Annotation type 'thread_disentanglement' already exists with ID: {existing.id}")
            return
        
        # Create the annotation type
        annotation_type = AnnotationType(
            name="thread_disentanglement",
            schema=schema
        )
        db.add(annotation_type)
        db.commit()
        db.refresh(annotation_type)
        
        print(f"Created annotation type 'thread_disentanglement' with ID: {annotation_type.id}")
    except Exception as e:
        print(f"Error creating annotation type: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_annotation_type() 