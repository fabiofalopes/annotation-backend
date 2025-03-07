# Database Schema Visualization

This directory contains visualizations of the database schema for the Text Annotation API.

## schema.png

This file shows the complete database schema, including all tables and their relationships. It was generated using SQLAlchemy's schema display tools.

Key features visible in the diagram:

1. **Joined Table Inheritance** - The inheritance hierarchy for annotations is clearly visible, with `BaseAnnotation` as the parent class and specialized annotation types (`TextAnnotation`, `ThreadAnnotation`, `SentimentAnnotation`) as child classes.

2. **Relationships** - The diagram shows all relationships between tables, including foreign keys and many-to-many relationships.

3. **Data Types** - Each column's data type is displayed, making it easy to understand the structure of each table.

## How to Regenerate

To regenerate this visualization, run:

```bash
python scripts/visualize_schema.py
```

You can also specify a custom output path:

```bash
python scripts/visualize_schema.py custom_path.png
```

## Admin Interface

In addition to this static visualization, the application includes an admin interface that provides an interactive view of the database. To access it, run the application and navigate to `/admin` in your browser. 