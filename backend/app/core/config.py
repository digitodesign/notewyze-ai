from pydantic_settings import BaseSettings
from typing import Optional, List, Union
import os
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "NoteWyze AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Get the SQLAlchemy database URI, handling Render's postgres:// format."""
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set")
            
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set")
        
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))  # 30 days
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Rate Limiting
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "1000"))
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "BACKEND_CORS_ORIGINS",
            "http://localhost:3000,http://localhost:8000,http://localhost:19006"
        ).split(",")
    ]
    
    # AI Services
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    # Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str(50 * 1024 * 1024)))  # 50MB
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [".mp3", ".wav", ".m4a", ".ogg"]
    
    # Redis Cache (for rate limiting and session storage)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Environment and Debug
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Create a global settings instance
settings = get_settings()
