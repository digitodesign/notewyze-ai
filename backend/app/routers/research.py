from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.api.errors import NotFoundError
from app.api.responses import create_success_response
from app.api.pagination import PaginationParams, paginate_query
from app.crud.crud_research import research as crud_research
from app.models.user import User
from app.schemas.research import ResearchCreate, ResearchUpdate, Research

router = APIRouter()

@router.get("/", response_model=dict)
def get_research_papers(
    params: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get paginated research papers for the current user.
    """
    query = crud_research.get_multi_by_user(db, user_id=current_user.id)
    return create_success_response(
        data=paginate_query(query, params),
        message="Research papers retrieved successfully",
    )

@router.post("/", response_model=dict)
def create_research_paper(
    research_in: ResearchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new research paper recommendation.
    """
    research = crud_research.create_with_user(
        db=db,
        obj_in=research_in,
        user_id=current_user.id,
    )
    return create_success_response(
        data=research,
        message="Research paper created successfully",
    )

@router.get("/{research_id}", response_model=dict)
def get_research_paper(
    research_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific research paper by ID.
    """
    research = crud_research.get(db=db, id=research_id)
    if not research or research.user_id != current_user.id:
        raise NotFoundError(detail="Research paper not found")
    
    return create_success_response(
        data=research,
        message="Research paper retrieved successfully",
    )

@router.put("/{research_id}", response_model=dict)
def update_research_paper(
    research_id: int,
    research_in: ResearchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a research paper.
    """
    research = crud_research.get(db=db, id=research_id)
    if not research or research.user_id != current_user.id:
        raise NotFoundError(detail="Research paper not found")
    
    research = crud_research.update(
        db=db,
        db_obj=research,
        obj_in=research_in,
    )
    return create_success_response(
        data=research,
        message="Research paper updated successfully",
    )

@router.delete("/{research_id}", response_model=dict)
def delete_research_paper(
    research_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a research paper.
    """
    research = crud_research.get(db=db, id=research_id)
    if not research or research.user_id != current_user.id:
        raise NotFoundError(detail="Research paper not found")
    
    crud_research.remove(db=db, id=research_id)
    return create_success_response(
        message="Research paper deleted successfully",
    )
