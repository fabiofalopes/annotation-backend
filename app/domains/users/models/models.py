from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base
from app.domains.datasets.models.association import project_user_association

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="annotator")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    annotations = relationship("BaseAnnotation", back_populates="user")
    projects = relationship("Project", secondary=project_user_association, back_populates="users") 