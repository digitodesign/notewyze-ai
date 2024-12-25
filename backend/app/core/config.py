from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "NoteWyze AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://neondb_owner:Q7hH4oRvxBFU@ep-broad-leaf-a5fhnrtn.us-east-2.aws.neon.tech/neondb?sslmode=require"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "notewyze-development-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:19006",  # Expo web
        "exp://localhost:19000",   # Expo development
        "exp://192.168.0.*:19000",   # Expo on local network
        "exp://exp.host/@*/*",       # Expo hosted
        "*://*.onrender.com",        # Render.com domains
        "*://*.expo.dev",            # Expo domains
        "*://*.expo.io"              # Expo domains
    ]
    
    # AI Services
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyAbfLe7brc1AeMxsn6_iqqyL4h2F25fFaM")
    
    # Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Allow extra fields in environment variables

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Create a global settings instance
settings = get_settings()
