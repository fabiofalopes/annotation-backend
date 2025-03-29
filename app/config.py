from typing import Dict, List
from pydantic_settings import BaseSettings
from pydantic import Field

class ProjectTypes:
    """Project type constants"""
    CHAT_DISENTANGLEMENT = "chat_disentanglement"
    IMAGE_ANNOTATION = "image_annotation"
    TEXT_CLASSIFICATION = "text_classification"
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all available project types"""
        return [
            value for key, value in cls.__dict__.items()
            if not key.startswith('_') and isinstance(value, str)
        ]

class ContainerTypes:
    """Container type constants"""
    CHAT_ROOMS = "chat_rooms"
    IMAGE_COLLECTIONS = "image_collections"
    TEXT_DOCUMENTS = "text_documents"
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all available container types"""
        return [
            value for key, value in cls.__dict__.items()
            if not key.startswith('_') and isinstance(value, str)
        ]

class Settings(BaseSettings):
    """Application settings"""
    # Project type mappings
    PROJECT_TYPE_MAPPINGS: Dict[str, str] = Field(
        default={
            ProjectTypes.CHAT_DISENTANGLEMENT: ContainerTypes.CHAT_ROOMS,
            ProjectTypes.IMAGE_ANNOTATION: ContainerTypes.IMAGE_COLLECTIONS,
            ProjectTypes.TEXT_CLASSIFICATION: ContainerTypes.TEXT_DOCUMENTS,
        },
        description="Mapping between project types and their default container types"
    )
    
    # Import settings
    DEFAULT_BATCH_SIZE: int = Field(
        default=1000,
        description="Default batch size for imports"
    )
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Annotation Backend"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings() 