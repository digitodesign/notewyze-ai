from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.config import get_settings
from app.core.health import check_services, get_health_status
import logging
from datetime import datetime

settings = get_settings()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="NoteWyze AI - Your AI-powered study companion"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    """
    Root endpoint.
    """
    return {
        "message": "Welcome to NoteWyze AI API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return await get_health_status()

@app.get("/services-health")
async def services_health_check():
    """
    Check the health of all services
    """
    return await check_services()

@app.on_event("startup")
async def startup_event():
    """
    Initialize services on startup
    """
    from app.db.init import init_database
    if not init_database():
        logger.error("Failed to initialize database")
        # In production, you might want to exit here
        # sys.exit(1)
