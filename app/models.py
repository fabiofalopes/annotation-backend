from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Text, Boolean, func, Table, ARRAY
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# Association tables
project_users = Table(
    "project_users",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
)

class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="annotator")  # annotator, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    created_projects = relationship("Project", back_populates="created_by")
    projects = relationship("Project", secondary="project_users", back_populates="users")
    annotations = relationship("Annotation", back_populates="created_by")

class Project(Base):
    """Project model to group related data containers"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., "chat_disentanglement", "document_annotation"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="created_projects")
    users = relationship("User", secondary="project_users", back_populates="projects")
    containers = relationship("DataContainer", back_populates="project", cascade="all, delete-orphan")

class DataContainer(Base):
    """Generic container for any type of data (e.g., chat rooms, image sets)"""
    __tablename__ = "data_containers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String)  # Type of data container (e.g., "chat_rooms", "documents", etc.)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    json_schema = Column(JSON)  # JSON Schema defining the data structure
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="containers")
    items = relationship("DataItem", back_populates="container", cascade="all, delete-orphan")
    created_by = relationship("User")
    import_progress = relationship("ImportProgress", back_populates="container")

class DataItem(Base):
    """Individual item that can be annotated (e.g., message, image)"""
    __tablename__ = "data_items"

    id = Column(Integer, primary_key=True)
    container_id = Column(Integer, ForeignKey("data_containers.id"))
    content = Column(Text)  # The actual content to be annotated
    item_metadata = Column(JSON, nullable=True)  # Additional data about the item
    parent_id = Column(Integer, ForeignKey("data_items.id"), nullable=True)
    sequence = Column(Integer, nullable=True)  # For ordered data
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    container = relationship("DataContainer", back_populates="items")
    annotations = relationship("Annotation", back_populates="item", cascade="all, delete-orphan")
    parent = relationship("DataItem", remote_side=[id], backref="children")

class Annotation(Base):
    """Flexible annotation system for data items"""
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("data_items.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String, index=True)  # e.g., "thread", "sentiment"
    data = Column(JSON)  # The annotation data
    start_offset = Column(Integer, nullable=True)  # For text spans
    end_offset = Column(Integer, nullable=True)  # For text spans
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    item = relationship("DataItem", back_populates="annotations")
    created_by = relationship("User", back_populates="annotations")

class ImportProgress(Base):
    __tablename__ = "import_progress"

    id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    errors = Column(JSON, default=list)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    container_id = Column(Integer, ForeignKey("data_containers.id"), nullable=True)
    metadata_columns = Column(JSON, nullable=True)

    # Relationship with DataContainer
    container = relationship("DataContainer", back_populates="import_progress") 