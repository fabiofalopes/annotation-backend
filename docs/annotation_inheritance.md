# Annotation Inheritance Model

This document explains the joined table inheritance implementation for annotations in the application.

## Overview

We've implemented SQLAlchemy's joined table inheritance to create a hierarchy of annotation models. This approach allows us to:

1. Share common fields and behavior across all annotation types
2. Create specialized annotation types with type-specific fields
3. Query annotations polymorphically (get all annotations or specific types)
4. Maintain database normalization and efficiency

## Model Structure

### Base Annotation

The `BaseAnnotation` class serves as the parent class for all annotation types. It contains fields common to all annotations:

- `id`: Primary key
- `item_id`: Reference to the annotatable item
- `annotation_type_id`: Reference to the annotation type
- `created_by`: User who created the annotation
- `annotation_data`: Structured annotation data (JSON)
- `start_addr` and `end_addr`: Position/range in text
- `source`: Origin of the annotation ("created" or "loaded")
- `created_at`: Timestamp
- `type`: Discriminator column for inheritance

### Specialized Annotation Types

We've created several specialized annotation types that inherit from `BaseAnnotation`:

1. **TextAnnotation**
   - For more granular text annotations
   - Additional fields: `text_category`, `text_metadata`

2. **ThreadAnnotation**
   - For thread disentanglement annotations
   - Additional fields: `thread_id`, `confidence_score`

3. **SentimentAnnotation**
   - For sentiment analysis annotations
   - Additional fields: `sentiment`, `intensity`

## Database Schema

The joined table inheritance creates the following database tables:

1. `annotations`: Contains all common fields and a discriminator column
2. `text_annotations`: Contains text-specific fields with a foreign key to `annotations`
3. `thread_annotations`: Contains thread-specific fields with a foreign key to `annotations`
4. `sentiment_annotations`: Contains sentiment-specific fields with a foreign key to `annotations`

When you query a specialized annotation type, SQLAlchemy automatically joins the tables to retrieve all fields.

## Usage Examples

### Creating Annotations

```python
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
```

### Querying Annotations

```python
# Query all annotations regardless of type
all_annotations = db.query(BaseAnnotation).all()

# Query only text annotations
text_annotations = db.query(TextAnnotation).all()

# Query only thread annotations
thread_annotations = db.query(ThreadAnnotation).all()

# Query only sentiment annotations
sentiment_annotations = db.query(SentimentAnnotation).all()
```

## Extending the Model

To add a new annotation type:

1. Create a new class that inherits from `BaseAnnotation`
2. Define a table name and primary key that references the base table
3. Add type-specific fields
4. Set a unique polymorphic identity

Example:

```python
class EntityAnnotation(BaseAnnotation):
    """
    Entity recognition annotation class.
    """
    __tablename__ = "entity_annotations"
    
    @declared_attr
    def id(cls):
        return Column(Integer, ForeignKey("annotations.id"), primary_key=True)
    
    entity_type = Column(String)  # e.g., "person", "organization", "location"
    entity_id = Column(String, nullable=True)  # Reference to a knowledge base
    
    __mapper_args__ = {
        "polymorphic_identity": "entity_annotation",
    }
```

## Benefits of This Approach

1. **Code Organization**: Common code is in the base class, specialized code in subclasses
2. **Type Safety**: Each annotation type has its own class with specific fields
3. **Polymorphic Queries**: Query all annotations or specific types
4. **Database Efficiency**: Common fields are stored in one table, specialized fields in separate tables
5. **Extensibility**: Easy to add new annotation types without changing existing code 