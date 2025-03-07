from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base

class ModuleInterface(Base):
    """
    Represents a specific instance of a module interface with its configuration.
    """
    __tablename__ = "module_interfaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="module_interface") 