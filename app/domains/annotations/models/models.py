from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import relationship, declared_attr
from app.infrastructure.database import Base
from datetime import datetime

# Import related models to resolve relationships
from app.domains.datasets.models.models import DataItem
from app.domains.users.models.models import User

class AnnotationType(Base):
    """
    Defines the type of annotation (e.g., thread disentanglement, sentiment analysis).
    """
    __tablename__ = "annotation_types"

    id = Column(Integer, primary_key=True, index=True) # Unique identifier for the annotation type
    name = Column(String, index=True) # Name of the annotation type
    annotation_schema = Column(JSON)  # JSON schema for the annotation
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # Date and time the annotation type was created
    
    # Relationships
    annotations = relationship("BaseAnnotation", back_populates="annotation_type") # Relationship to the BaseAnnotation model

class BaseAnnotation(Base):
    """
    Base model for all annotations, supporting modular annotation types.
    Uses joined table inheritance to allow specialized annotation types.
    """
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True) # Unique identifier for the annotation
    item_id = Column(Integer, ForeignKey("data_items.id"))  # Link to DataItem (which includes Turn)
    annotation_type_id = Column(Integer, ForeignKey("annotation_types.id"))
    created_by = Column(Integer, ForeignKey("users.id")) # User who created the annotation
    annotation_data = Column(JSON)  # Structured annotation data
    start_addr = Column(Integer, nullable=True)  # Start address/position in text
    end_addr = Column(Integer, nullable=True)  # End address/position in text
    source = Column(String, default="created")  # "created" or "loaded"
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # Date and time the annotation was created
    
    # Discriminator column for inheritance
    type = Column(String(50))
    
    # Relationships
    data_item = relationship("DataItem", back_populates="annotations")
    annotation_type = relationship("AnnotationType", back_populates="annotations") # Relationship to the AnnotationType model
    user = relationship("User", back_populates="annotations")  # Relationship to the User model
    
    __mapper_args__ = {
        "polymorphic_identity": "base_annotation",
        "polymorphic_on": type
    }

class ThreadAnnotation(BaseAnnotation):
    """
    Thread disentanglement annotation class.
    Uses joined table inheritance with BaseAnnotation.
    Typically refers to the whole message (full address range).
    """
    __tablename__ = "thread_annotations"
    
    @declared_attr
    def id(cls):
        return Column(Integer, ForeignKey("annotations.id"), primary_key=True)
    
    thread_id = Column(String, index=True)  # ID of the thread this message belongs to
    confidence_score = Column(Integer, nullable=True)  # Annotator confidence (1-5)
    
    __mapper_args__ = {
        "polymorphic_identity": "thread_annotation",
    }

class SentimentAnnotation(BaseAnnotation):
    """
    Sentiment analysis annotation class.
    Uses joined table inheritance with BaseAnnotation.
    Could be applied to entire messages or specific portions.
    """
    __tablename__ = "sentiment_annotations"
    
    @declared_attr
    def id(cls):
        return Column(Integer, ForeignKey("annotations.id"), primary_key=True)
    
    sentiment = Column(String)  # e.g., "positive", "negative", "neutral"
    intensity = Column(Integer, nullable=True)  # Intensity score (1-5)
    
    __mapper_args__ = {
        "polymorphic_identity": "sentiment_annotation",
    }