from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.crud.crud_user import user as crud_user
from app.schemas.user import User, UserUpdate

router = APIRouter()

@router.get("/users/me", response_model=User)
def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user."""
    return current_user

@router.put("/users/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update own user."""
    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user
