import logging
from typing import Dict, Any
import httpx
import google.generativeai as genai
from app.db.session import check_db_connection
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

async def check_gemini_connection() -> bool:
    """Check if Google Gemini API is accessible."""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("test")
        return True
    except Exception as e:
        logger.error(f"Gemini connection check failed: {str(e)}")
        return False

async def check_frontend_connection() -> bool:
    """Check if frontend is accessible."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3000/health")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Frontend connection check failed: {str(e)}")
        return False

async def check_services() -> Dict[str, Any]:
    """Check all service connections."""
    database_ok = check_db_connection()
    gemini_ok = await check_gemini_connection()
    frontend_ok = await check_frontend_connection()

    status = "healthy" if all([database_ok, gemini_ok, frontend_ok]) else "unhealthy"
    
    return {
        "status": status,
        "services": {
            "database": {
                "status": "up" if database_ok else "down",
                "type": "neon",
                "host": "ep-broad-leaf-a5fhnrtn.us-east-2.aws.neon.tech"
            },
            "gemini": {
                "status": "up" if gemini_ok else "down",
                "type": "api"
            },
            "frontend": {
                "status": "up" if frontend_ok else "down",
                "url": "http://localhost:3000"
            }
        },
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
