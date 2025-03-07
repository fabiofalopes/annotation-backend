"""
Script to initialize the database tables.
"""
from app.infrastructure.database import create_tables

def init_db():
    """Initialize the database by creating all tables."""
    print("Creating database tables...")
    create_tables()
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 