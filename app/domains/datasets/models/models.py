from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship, declared_attr
from app.infrastructure.database import Base

# Import related models to resolve relationships
from app.domains.module_interfaces.models.models import ModuleInterface
from app.domains.users.models.models import User
from app.domains.datasets.models.association import project_user_association

class Project(Base):
    """
    Represents a project that organizes datasets and users for a specific module interface.
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    module_interface_id = Column(Integer, ForeignKey("module_interfaces.id"), nullable=True)  # Make nullable
    project_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    datasets = relationship("Dataset", back_populates="project", cascade="all, delete-orphan")
    module_interface = relationship("ModuleInterface", back_populates="projects")
    users = relationship("User", secondary=project_user_association, back_populates="projects")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


# --- Dataset and DataItem ---

class Dataset(Base):
    """
    Represents a dataset within a project.
    For chat disentanglement, this could represent a chatroom.
    """
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))  # Link to Project
    name = Column(String, index=True)
    dataset_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="datasets")
    data_items = relationship("DataItem", back_populates="dataset", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="dataset", cascade="all, delete-orphan")


class DataItem(Base):
    """
    Represents an individual item of data that can be annotated.
    This is the base class for all annotatable items in the system.
    """
    __tablename__ = "data_items"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    identifier = Column(String, index=True)  # External identifier
    content = Column(Text)  # Raw content (can be text, JSON, etc.)
    item_metadata = Column(JSON, nullable=True)
    sequence = Column(Integer, nullable=True)  # Optional ordering
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Discriminator column for inheritance
    type = Column(String(50))

    # Relationships
    dataset = relationship("Dataset", back_populates="data_items")
    annotations = relationship("BaseAnnotation", back_populates="data_item", cascade="all, delete-orphan")
    
    __mapper_args__ = {
        "polymorphic_identity": "data_item",
        "polymorphic_on": type
    }


class Turn(DataItem):
    """
    Represents a turn (message) in a conversation that can be annotated.
    Inherits from DataItem to maintain a consistent annotation structure.
    """
    __tablename__ = "turns"
    
    @declared_attr
    def id(cls):
        return Column(Integer, ForeignKey("data_items.id"), primary_key=True)
    
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    turn_id = Column(String)      # Original turn ID from CSV
    user_id = Column(String)      # User who sent the message
    reply_to_turn = Column(String, nullable=True)  # ID of the turn this is replying to
    
    # Relationships
    conversation = relationship("Conversation", back_populates="turns")
    
    __mapper_args__ = {
        "polymorphic_identity": "turn",
    }


class Conversation(Base):
    """
    Represents a conversation within a dataset (chatroom).
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))  # Link to Dataset instead of Chatroom
    identifier = Column(String, index=True)  # Unique ID for the conversation
    content = Column(JSON)  # Store raw CSV
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    dataset = relationship("Dataset", back_populates="conversations")
    turns = relationship("Turn", back_populates="conversation", cascade="all, delete-orphan") 