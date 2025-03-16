#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

import graphviz
from sqlalchemy import inspect
from sqlalchemy.orm import class_mapper

from app.models import Base, User, Project, DataContainer, DataItem, Annotation
from app.schemas import (
    UserCreate, UserResponse,
    ProjectCreate, ProjectResponse, ProjectWithContainers,
    DataContainerCreate, DataContainerResponse, DataContainerWithItems,
    DataItemCreate, DataItemResponse, DataItemWithAnnotations,
    AnnotationCreate, AnnotationResponse,
    ChatRoomSchema, ChatTurn
)

def create_model_diagram():
    """Create a diagram of SQLAlchemy models and their relationships."""
    dot = graphviz.Digraph(comment='Database Models')
    dot.attr(rankdir='LR')

    # Process each model
    models = [User, Project, DataContainer, DataItem, Annotation]
    for model in models:
        mapper = class_mapper(model)
        table_name = mapper.class_.__name__

        # Create node for the table
        attributes = []
        for column in mapper.columns:
            nullable = "nullable" if column.nullable else "not null"
            default = f"default={column.default.arg}" if column.default else ""
            attributes.append(f"+ {column.name}: {column.type} ({nullable} {default})")

        label = f"{table_name}|" + "\\l".join(attributes) + "\\l"
        dot.node(table_name, label, shape='record')

        # Add relationships
        for relationship in mapper.relationships:
            target = relationship.mapper.class_.__name__
            dot.edge(table_name, target, 
                    label=f"{relationship.key}\\n({relationship.direction.name})")

    return dot

def create_schema_diagram():
    """Create a diagram of Pydantic schemas and their inheritance."""
    dot = graphviz.Digraph(comment='API Schemas')
    dot.attr(rankdir='LR')

    # Process each schema
    schemas = [
        UserCreate, UserResponse,
        ProjectCreate, ProjectResponse, ProjectWithContainers,
        DataContainerCreate, DataContainerResponse, DataContainerWithItems,
        DataItemCreate, DataItemResponse, DataItemWithAnnotations,
        AnnotationCreate, AnnotationResponse,
        ChatRoomSchema, ChatTurn
    ]

    for schema in schemas:
        schema_name = schema.__name__

        # Get fields from schema
        fields = []
        for name, field in schema.__fields__.items():
            field_type = field.annotation.__name__ if hasattr(field.annotation, '__name__') else str(field.annotation)
            required = "required" if field.is_required() else "optional"
            fields.append(f"+ {name}: {field_type} ({required})")

        label = f"{schema_name}|" + "\\l".join(fields) + "\\l"
        dot.node(schema_name, label, shape='record')

        # Add inheritance relationships
        for base in schema.__bases__:
            if base.__name__ != 'BaseModel':
                dot.edge(base.__name__, schema_name, style='dashed')

    return dot

def main():
    """Generate schema visualizations."""
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / 'docs' / 'schema'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate model diagram
    model_diagram = create_model_diagram()
    model_diagram.render(str(output_dir / 'models'), format='png', cleanup=True)
    print(f"Generated models diagram at {output_dir}/models.png")

    # Generate schema diagram
    schema_diagram = create_schema_diagram()
    schema_diagram.render(str(output_dir / 'schemas'), format='png', cleanup=True)
    print(f"Generated schemas diagram at {output_dir}/schemas.png")

    # Generate combined diagram
    combined = graphviz.Digraph(comment='Combined Models and Schemas')
    combined.attr(rankdir='LR')

    with combined.subgraph(name='cluster_0') as s0:
        s0.attr(label='Database Models')
        s0.node_attr['style'] = 'filled'
        s0.node_attr['fillcolor'] = 'lightblue'
        model_diagram = create_model_diagram()
        s0.subgraph(model_diagram)

    with combined.subgraph(name='cluster_1') as s1:
        s1.attr(label='API Schemas')
        s1.node_attr['style'] = 'filled'
        s1.node_attr['fillcolor'] = 'lightgreen'
        schema_diagram = create_schema_diagram()
        s1.subgraph(schema_diagram)

    combined.render(str(output_dir / 'combined'), format='png', cleanup=True)
    print(f"Generated combined diagram at {output_dir}/combined.png")

if __name__ == '__main__':
    main() 