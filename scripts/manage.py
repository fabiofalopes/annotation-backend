"""
Management script for the application.
Provides commands for database initialization and user management.
"""
import typer
from sqlalchemy.orm import Session
import os

from app.infrastructure.database import engine, Base, SessionLocal
# Import all models to ensure they are registered with Base
from app.domains.users.models.models import User
from app.domains.annotations.models.models import BaseAnnotation, TextAnnotation, ThreadAnnotation, SentimentAnnotation
from app.domains.datasets.models.models import Dataset, DataUnit, AnnotatableItem

app = typer.Typer()

@app.command()
def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    typer.echo("Tables created successfully.")

@app.command()
def create_admin_user(username: str, password: str):
    """Create an admin user."""
    from app.domains.users.services.user_service import UserService
    from app.domains.users.schemas.schemas import UserCreate
    
    db = SessionLocal()
    try:
        user_create = UserCreate(username=username, password=password)
        user = UserService.create_user(db, user_create, role="admin")
        typer.echo(f"Admin user '{username}' created successfully.")
    except Exception as e:
        typer.echo(f"Error creating admin user: {e}")
    finally:
        db.close()

@app.command()
def list_users():
    """List all users in the database."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            typer.echo("No users found.")
            return
        
        typer.echo(f"Found {len(users)} users:")
        for user in users:
            typer.echo(f"ID: {user.id}, Username: {user.username}, Role: {user.role}")
    except Exception as e:
        typer.echo(f"Error listing users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    app() 