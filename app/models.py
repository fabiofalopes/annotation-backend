from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Text, Boolean, func, Table
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# Association tables
project_user = Table(
    "project_user",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id")),
    Column("user_id", Integer, ForeignKey("users.id"))
)

class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default='annotator')  # Values: 'annotator' or 'admin'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    projects = relationship("Project", secondary=project_user, back_populates="users")
    annotations = relationship("Annotation", back_populates="created_by")

class Project(Base):
    """Project model to group related data containers"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    type = Column(String, index=True)  # Type of project (e.g., "chat_disentanglement")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("User", secondary=project_user, back_populates="projects")
    containers = relationship("DataContainer", back_populates="project")

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