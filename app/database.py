import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models import Base
from app.settings import settings

# Ensure the data directory exists
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Create engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    from app.models import Base
    Base.metadata.drop_all(bind=engine)  # Drop all tables
    Base.metadata.create_all(bind=engine)  # Create all tables 