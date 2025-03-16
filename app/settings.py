from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    How it works:
    - Field names are automatically mapped to environment variables
    - For example, 'database_url' looks for the 'DATABASE_URL' environment variable
    - Pydantic automatically converts field_name to FIELD_NAME for env var lookup
    - Values are loaded from environment variables or .env file
    - No need to manually use os.getenv() for each setting
    """
    
    # Database
    database_url: str
    
    # Security
    secret_key: str
    environment: str
    
    # Admin credentials
    admin_username: str
    admin_password: str
    admin_email: str
    
    # JWT
    jwt_algorithm: str = "HS256"  # Reasonable default
    access_token_expire_minutes: int = 30  # Reasonable default
    
    # Logging
    log_level: str

    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings() 