from pydantic_settings import BaseSettings
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/annotation_db")
    
    # Project type mappings
    PROJECT_TYPES: Dict[str, Dict[str, Any]] = {
        "chat_disentanglement": {
            "name": "Chat Disentanglement",
            "description": "Analyze and organize chat conversations into threads",
            "container_types": ["chat_rooms"],
            "annotation_types": ["thread"]
        }
    }
    
    # Import settings
    IMPORT_BATCH_SIZE: int = 1000
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Annotation Backend"
    
    class Config:
        case_sensitive = True

# Create global settings instance
settings = Settings() 