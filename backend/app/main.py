from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api import api_router
from app.core.config import settings
from app.core.health import check_services, get_health_status
from app.api.errors import APIError
import logging
import time
from typing import Callable
import uvicorn

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="NoteWyze AI - Your AI-powered study companion",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Custom middleware for request logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    """Log request details and timing."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} "
        f"[{response.status_code}] {duration:.2f}s"
    )
    
    return response

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

# Error handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """Handle custom API errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return await get_health_status()

@app.get("/services-health")
async def services_health_check():
    """Detailed services health check."""
    return await check_services()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode")
    
    # Verify database connection
    try:
        from app.db.database import engine
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

    # Initialize other services as needed
    logger.info("All services initialized")
