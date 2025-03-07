import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings."""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Text Annotation API"
    PROJECT_DESCRIPTION: str = "API for text annotation tasks"
    VERSION: str = "0.1.0"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/test.db")
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

# Create global settings object
settings = Settings() 