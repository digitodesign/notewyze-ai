"""
API package initialization.
"""
from fastapi import APIRouter

from app.routers import (
    auth,
    users,
    recordings,
    quizzes,
    research,
    study
)

from .errors import (
    APIError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
)
from .responses import (
    create_response,
    create_success_response,
    create_error_response,
)
from .pagination import (
    PaginationParams,
    paginate_query,
)

# Create API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(recordings.router, prefix="/recordings", tags=["recordings"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(study.router, prefix="/study", tags=["study"])

__all__ = [
    "api_router",
    "APIError",
    "NotFoundError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "create_response",
    "create_success_response",
    "create_error_response",
    "PaginationParams",
    "paginate_query",
]
