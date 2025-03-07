#!/usr/bin/env python
"""
Script to generate a visualization of the database schema.
"""
import sys
import os
import subprocess
import time

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database import Base, engine
from app.domains.users.models.models import User
from app.domains.annotations.models.models import BaseAnnotation, ThreadAnnotation, SentimentAnnotation, AnnotationType
from app.domains.datasets.models.models import Project, Dataset, DataItem, Turn, Conversation
from app.domains.module_interfaces.models.models import ModuleInterface
from app.domains.datasets.models.association import project_user_association

def visualize_schema():
    """Generate a visualization of the database schema."""
    try:
        # Check if sqlalchemy_schemadisplay is installed
        import sqlalchemy_schemadisplay
    except ImportError:
        print("sqlalchemy_schemadisplay is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sqlalchemy_schemadisplay"])
        import sqlalchemy_schemadisplay
    
    try:
        # Check if pydot is installed
        import pydot
    except ImportError:
        print("pydot is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pydot"])
        import pydot
    
    # Create the directory if it doesn't exist
    os.makedirs("docs/schema", exist_ok=True)
    
    # Create the schema diagram
    from sqlalchemy_schemadisplay import create_schema_graph
    
    # Generate the graph
    graph = create_schema_graph(
        metadata=Base.metadata,
        show_datatypes=True,
        show_indexes=True,
        rankdir='LR',  # Left to right
        concentrate=False,
        engine=engine  # Add the engine parameter
    )
    
    # Generate a timestamp for the filename to ensure we get a new file
    timestamp = int(time.time())
    
    # Save the graph to a file with a timestamp
    filename = f'docs/schema/schema_{timestamp}.png'
    graph.write_png(filename)
    
    # Also save to the standard filename for consistency
    graph.write_png('docs/schema/schema.png')
    
    print(f"Schema visualization saved to {filename} and docs/schema/schema.png")

if __name__ == "__main__":
    visualize_schema() 