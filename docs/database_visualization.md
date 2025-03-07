# Database Visualization Tools

This document explains the database visualization tools available in the Text Annotation API.

## Overview

Understanding the database schema is crucial for development, debugging, and optimization. The Text Annotation API provides two main ways to visualize the database schema:

1. **Static Schema Visualization** - A PNG image showing the complete database schema
2. **Interactive Admin Interface** - A web-based admin interface for exploring and managing the database

## Static Schema Visualization

The static schema visualization is a PNG image that shows all tables, columns, and relationships in the database. It's particularly useful for:

- Understanding the overall structure of the database
- Documenting the database schema
- Analyzing relationships between tables
- Identifying potential optimization opportunities

### Viewing the Schema

The schema visualization is stored in `docs/images/schema.png`. You can open this file with any image viewer.

### Regenerating the Schema

If you make changes to the database models, you'll need to regenerate the schema visualization. To do this, run:

```bash
python scripts/visualize_schema.py
```

This will update the `docs/images/schema.png` file with the latest schema.

### Understanding the Schema

The schema visualization uses the following conventions:

- **Tables** are represented as boxes with the table name at the top
- **Columns** are listed inside each box, with their data types
- **Primary keys** are marked with a key icon
- **Foreign keys** are shown as arrows pointing to the referenced table
- **Inheritance relationships** are shown as special arrows (for the joined table inheritance used in annotations)

## Interactive Admin Interface

The admin interface provides a web-based UI for exploring and managing the database. It's particularly useful for:

- Browsing and searching data
- Adding, editing, and deleting records
- Visualizing relationships between tables
- Testing and debugging

### Accessing the Admin Interface

To access the admin interface:

1. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000/admin/
   ```

3. Log in with your admin credentials

### Features of the Admin Interface

The admin interface provides the following features:

- **Dashboard** - An overview of the database
- **Model browsers** - Interfaces for browsing and editing each model
- **Relationship visualization** - Visual representation of relationships between records
- **Search** - Ability to search across models
- **Filtering** - Advanced filtering options for each model

## Joined Table Inheritance Visualization

The database schema uses SQLAlchemy's joined table inheritance for annotations. This is clearly visible in both visualization tools:

- In the static schema, you can see the `annotations` table as the parent, with `text_annotations`, `thread_annotations`, and `sentiment_annotations` as child tables.
- In the admin interface, you can browse both the base `BaseAnnotation` model and the specialized annotation types.

This inheritance structure allows for:

1. Shared common fields across all annotation types
2. Type-specific fields for specialized annotation types
3. Polymorphic queries (querying all annotations or specific types)
4. Database normalization and efficiency

## Optimization Insights

The visualization tools can help identify potential optimization opportunities:

- **Missing indexes** - Look for columns that are frequently queried but not indexed
- **Complex relationships** - Identify tables with many relationships that might benefit from denormalization
- **Inheritance overhead** - Evaluate whether the joined table inheritance is appropriate for your use case

## Conclusion

The database visualization tools provide valuable insights into the structure and relationships of the database. Use them regularly to understand, document, and optimize your database schema. 