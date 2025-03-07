#!/usr/bin/env python
"""
Script to create database tables for our models.
"""
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database import Base, engine
from app.domains.users.models.models import User
from app.domains.annotations.models.models import BaseAnnotation, ThreadAnnotation, TextAnnotation, SentimentAnnotation, AnnotationType
from app.domains.datasets.models.models import Project, Dataset, DataItem, Turn, Conversation
from app.domains.module_interfaces.models.models import ModuleInterface
from app.domains.datasets.models.association import project_user_association

def create_tables():
    """Create all tables in the database."""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables() 