"""
Example script demonstrating how to use the annotation inheritance models.
"""
from sqlalchemy.orm import Session
from app.infrastructure.database import SessionLocal
from app.domains.annotations.models import (
    BaseAnnotation,
    TextAnnotation,
    ThreadAnnotation,
    SentimentAnnotation,
    AnnotationType
)
# Import related models to resolve relationships
from app.domains.datasets.models.models import AnnotatableItem, DataUnit, Dataset
from app.domains.users.models.models import User
from app.domains.module_interfaces.models.models import ModuleInterface

def create_annotation_types(db: Session):
    """Create example annotation types"""
    # Create annotation types if they don't exist
    text_type = db.query(AnnotationType).filter(AnnotationType.name == "text").first()
    if not text_type:
        text_type = AnnotationType(
            name="text",
            schema={"type": "object", "properties": {"label": {"type": "string"}}}
        )
        db.add(text_type)
    
    thread_type = db.query(AnnotationType).filter(AnnotationType.name == "thread").first()
    if not thread_type:
        thread_type = AnnotationType(
            name="thread",
            schema={"type": "object", "properties": {"thread_id": {"type": "string"}}}
        )
        db.add(thread_type)
    
    sentiment_type = db.query(AnnotationType).filter(AnnotationType.name == "sentiment").first()
    if not sentiment_type:
        sentiment_type = AnnotationType(
            name="sentiment",
            schema={"type": "object", "properties": {"sentiment": {"type": "string"}}}
        )
        db.add(sentiment_type)
    
    db.commit()
    return text_type, thread_type, sentiment_type

def create_example_annotations(db: Session, item_id: int, user_id: int):
    """Create example annotations using the inheritance hierarchy"""
    # First create annotation types
    text_type, thread_type, sentiment_type = create_annotation_types(db)
    
    # Create a text annotation
    text_annotation = TextAnnotation(
        item_id=item_id,
        annotation_type_id=text_type.id,
        created_by=user_id,
        start_addr=10,
        end_addr=20,
        annotation_data={"label": "important"},
        text_category="entity",
        text_metadata={"confidence": 0.95}
    )
    db.add(text_annotation)
    
    # Create a thread annotation
    thread_annotation = ThreadAnnotation(
        item_id=item_id,
        annotation_type_id=thread_type.id,
        created_by=user_id,
        # For thread annotations, we might use null addresses to indicate the entire message
        start_addr=None,
        end_addr=None,
        annotation_data={"thread_id": "thread-123"},
        thread_id="thread-123",
        confidence_score=4
    )
    db.add(thread_annotation)
    
    # Create a sentiment annotation
    sentiment_annotation = SentimentAnnotation(
        item_id=item_id,
        annotation_type_id=sentiment_type.id,
        created_by=user_id,
        start_addr=5,
        end_addr=15,
        annotation_data={"sentiment": "positive"},
        sentiment="positive",
        intensity=4
    )
    db.add(sentiment_annotation)
    
    db.commit()
    return text_annotation, thread_annotation, sentiment_annotation

def query_annotations(db: Session):
    """Demonstrate querying annotations using the inheritance hierarchy"""
    # Query all annotations regardless of type
    all_annotations = db.query(BaseAnnotation).all()
    print(f"All annotations ({len(all_annotations)}):")
    for annotation in all_annotations:
        print(f"  - {annotation.__class__.__name__} (ID: {annotation.id})")
    
    # Query only text annotations
    text_annotations = db.query(TextAnnotation).all()
    print(f"\nText annotations ({len(text_annotations)}):")
    for annotation in text_annotations:
        print(f"  - Category: {annotation.text_category}, Range: {annotation.start_addr}-{annotation.end_addr}")
    
    # Query only thread annotations
    thread_annotations = db.query(ThreadAnnotation).all()
    print(f"\nThread annotations ({len(thread_annotations)}):")
    for annotation in thread_annotations:
        print(f"  - Thread ID: {annotation.thread_id}, Confidence: {annotation.confidence_score}")
    
    # Query only sentiment annotations
    sentiment_annotations = db.query(SentimentAnnotation).all()
    print(f"\nSentiment annotations ({len(sentiment_annotations)}):")
    for annotation in sentiment_annotations:
        print(f"  - Sentiment: {annotation.sentiment}, Intensity: {annotation.intensity}")

def main():
    """Main function to demonstrate annotation inheritance"""
    db = SessionLocal()
    try:
        # For this example, we'll use placeholder IDs
        # In a real application, you would use actual item and user IDs
        item_id = 1
        user_id = 1
        
        # Create example annotations
        create_example_annotations(db, item_id, user_id)
        
        # Query and display annotations
        query_annotations(db)
    finally:
        db.close()

if __name__ == "__main__":
    main() 