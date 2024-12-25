"""
API pagination utilities.
"""
from typing import Any, Dict, Generic, List, Optional, TypeVar

from fastapi import Query
from pydantic.generics import GenericModel
from sqlalchemy.orm import Query as SQLAQuery

DataT = TypeVar("DataT")


class PaginationParams:
    """
    Pagination parameters.
    """
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.per_page = per_page

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class PageInfo(BaseModel):
    """
    Pagination information.
    """
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(GenericModel, Generic[DataT]):
    """
    Paginated response model.
    """
    items: List[DataT]
    page_info: PageInfo


def paginate_query(
    query: SQLAQuery,
    params: PaginationParams,
) -> Dict[str, Any]:
    """
    Paginate a SQLAlchemy query.
    """
    total = query.count()
    items = query.offset(params.offset).limit(params.per_page).all()
    
    pages = (total + params.per_page - 1) // params.per_page
    has_next = params.page < pages
    has_prev = params.page > 1

    return {
        "items": items,
        "page_info": PageInfo(
            total=total,
            page=params.page,
            per_page=params.per_page,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev,
        ),
    }
