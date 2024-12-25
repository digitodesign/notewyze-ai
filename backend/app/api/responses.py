"""
API response utilities.
"""
from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel


DataT = TypeVar("DataT")


class ResponseMetadata(BaseModel):
    """
    Response metadata model.
    """
    code: str = "SUCCESS"
    message: Optional[str] = None


class Response(GenericModel, Generic[DataT]):
    """
    Standard API response model.
    """
    data: Optional[DataT] = None
    meta: ResponseMetadata = ResponseMetadata()


def create_response(
    data: Any = None,
    message: Optional[str] = None,
    code: str = "SUCCESS",
) -> Dict[str, Any]:
    """
    Create a standardized API response.
    """
    return Response[Any](
        data=data,
        meta=ResponseMetadata(
            code=code,
            message=message,
        ),
    ).dict()


def create_success_response(
    data: Any = None,
    message: str = "Operation successful",
) -> Dict[str, Any]:
    """
    Create a success response.
    """
    return create_response(
        data=data,
        message=message,
        code="SUCCESS",
    )


def create_error_response(
    message: str,
    code: str = "ERROR",
) -> Dict[str, Any]:
    """
    Create an error response.
    """
    return create_response(
        message=message,
        code=code,
    )
