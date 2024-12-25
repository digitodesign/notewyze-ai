from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_study
from app.schemas import study as study_schemas
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/sessions", response_model=study_schemas.StudySession)
def start_study_session(
    *,
    db: Session = Depends(deps.get_db),
    session_in: study_schemas.StudySessionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Start a new study session.
    """
    return crud_study.create_with_owner(
        db=db,
        obj_in=session_in,
        owner_id=current_user.id
    )

@router.put("/sessions/{session_id}", response_model=study_schemas.StudySession)
def end_study_session(
    *,
    db: Session = Depends(deps.get_db),
    session_id: int,
    session_in: study_schemas.StudySessionUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    End a study session and update notes.
    """
    session = crud_study.get(db=db, id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_study.update(db=db, db_obj=session, obj_in=session_in)

@router.get("/sessions/recording/{recording_id}", response_model=List[study_schemas.StudySession])
def read_sessions_by_recording(
    recording_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all study sessions for a specific recording.
    """
    return crud_study.get_by_recording(
        db=db,
        recording_id=recording_id,
        user_id=current_user.id
    )

@router.get("/stats/recording/{recording_id}", response_model=study_schemas.StudyStats)
def get_recording_stats(
    recording_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get study statistics for a specific recording.
    """
    return crud_study.get_recording_stats(
        db=db,
        recording_id=recording_id,
        user_id=current_user.id
    )

@router.get("/stats/overall", response_model=study_schemas.StudyStats)
def get_overall_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall study statistics for the user.
    """
    return crud_study.get_overall_stats(
        db=db,
        user_id=current_user.id
    )
