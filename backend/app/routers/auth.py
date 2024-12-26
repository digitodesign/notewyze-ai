from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.api.errors import AuthenticationError
from app.api.responses import create_success_response
from app.core import security
from app.core.config import settings
from app.crud.crud_user import user as crud_user
from app.schemas.token import Token
from app.schemas.user import UserCreate

router = APIRouter()

@router.post("/login", response_model=dict)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise AuthenticationError(detail="Incorrect email or password")
    elif not user.is_active:
        raise AuthenticationError(detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    return create_success_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        },
        message="Successfully logged in",
    )

@router.post("/signup", response_model=dict)
def signup(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
):
    """
    Create new user.
    """
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise AuthenticationError(
            detail="The user with this email already exists in the system",
        )
    
    user = crud_user.create(db, obj_in=user_in)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    return create_success_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        },
        message="User created successfully",
    )

@router.post("/test-token", response_model=dict)
def test_token(current_user = Depends(get_current_active_user)):
    """
    Test access token.
    """
    return create_success_response(
        data=current_user,
        message="Token is valid",
    )
