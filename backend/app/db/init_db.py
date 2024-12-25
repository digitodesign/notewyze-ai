import logging
from sqlalchemy.orm import Session

from app.crud.crud_user import user as crud_user
from app.schemas.user import UserCreate
from app.core.config import get_settings
from app.db.session import engine
from app.models.base import Base

settings = get_settings()
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create initial superuser if needed
    user = crud_user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if not user and settings.FIRST_SUPERUSER_EMAIL:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            full_name="Initial Super User"
        )
        user = crud_user.create(db, obj_in=user_in)
        logger.info(f"Created initial superuser: {user.email}")

def create_initial_data(db: Session) -> None:
    """
    Create initial data for development/testing.
    Only runs if ENVIRONMENT is "development"
    """
    if settings.ENVIRONMENT == "development":
        # Add any initial data creation here
        pass
