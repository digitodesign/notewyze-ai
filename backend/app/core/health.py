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

async def check_external_connectivity() -> bool:
    """Check if external internet connectivity is available."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://www.google.com")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"External connectivity check failed: {str(e)}")
        return False

async def get_health_status() -> Dict[str, Any]:
    """Get health status of all services."""
    db_healthy = await check_db_connection()
    gemini_healthy = await check_gemini_connection()
    external_connectivity = await check_external_connectivity()
    
    all_healthy = all([db_healthy, external_connectivity])
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "services": {
            "database": "healthy" if db_healthy else "unhealthy",
            "gemini": "healthy" if gemini_healthy else "unhealthy",
            "external_connectivity": "healthy" if external_connectivity else "unhealthy"
        },
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
