"""
API error handling utilities.
"""
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """
    Standard error response model.
    """
    detail: str
    code: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


class APIError(HTTPException):
    """
    Custom API error that includes error code and parameters.
    """
    def __init__(
        self,
        status_code: int,
        detail: str,
        code: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=ErrorResponse(
                detail=detail,
                code=code,
                params=params,
            ).dict(),
        )


class NotFoundError(APIError):
    """
    Resource not found error.
    """
    def __init__(
        self,
        detail: str = "Resource not found",
        code: Optional[str] = "NOT_FOUND",
        params: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            code=code,
            params=params,
        )


class ValidationError(APIError):
    """
    Data validation error.
    """
    def __init__(
        self,
        detail: str = "Validation error",
        code: Optional[str] = "VALIDATION_ERROR",
        params: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code=code,
            params=params,
        )


class AuthenticationError(APIError):
    """
    Authentication error.
    """
    def __init__(
        self,
        detail: str = "Authentication failed",
        code: Optional[str] = "AUTHENTICATION_ERROR",
        params: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code=code,
            params=params,
        )


class AuthorizationError(APIError):
    """
    Authorization error.
    """
    def __init__(
        self,
        detail: str = "Not authorized",
        code: Optional[str] = "AUTHORIZATION_ERROR",
        params: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            code=code,
            params=params,
        )
