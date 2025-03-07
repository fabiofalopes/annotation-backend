from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class
Base = declarative_base()

def create_tables():
    """Create database tables."""
    # Import models to ensure they are registered with Base
    from app.domains.users.models import models
    from app.domains.annotations.models import models
    from app.domains.datasets.models import models
    from app.domains.module_interfaces.models import models
    
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    """
    Dependency for getting a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 