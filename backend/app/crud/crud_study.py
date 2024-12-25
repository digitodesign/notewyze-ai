from typing import List, Optional
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.crud.base import CRUDBase
from app.models.study import StudySession
from app.schemas.study import StudySessionCreate, StudySessionUpdate, StudyStats

class CRUDStudy(CRUDBase[StudySession, StudySessionCreate, StudySessionUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: StudySessionCreate, owner_id: int
    ) -> StudySession:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_recording(
        self, db: Session, *, recording_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[StudySession]:
        return (
            db.query(self.model)
            .filter(
                StudySession.recording_id == recording_id,
                StudySession.user_id == user_id
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_recording_stats(
        self, db: Session, *, recording_id: int, user_id: int
    ) -> StudyStats:
        query = db.query(
            func.count(StudySession.id).label("total_sessions"),
            func.sum(StudySession.duration).label("total_duration"),
            func.max(StudySession.end_time).label("last_session")
        ).filter(
            StudySession.recording_id == recording_id,
            StudySession.user_id == user_id,
            StudySession.duration.isnot(None)
        )
        
        result = query.first()
        total_sessions = result.total_sessions or 0
        total_duration = result.total_duration or 0.0
        
        return StudyStats(
            total_sessions=total_sessions,
            total_duration=total_duration,
            average_session_duration=total_duration / total_sessions if total_sessions > 0 else 0.0,
            last_session=result.last_session
        )

    def get_overall_stats(
        self, db: Session, *, user_id: int
    ) -> StudyStats:
        query = db.query(
            func.count(StudySession.id).label("total_sessions"),
            func.sum(StudySession.duration).label("total_duration"),
            func.max(StudySession.end_time).label("last_session")
        ).filter(
            StudySession.user_id == user_id,
            StudySession.duration.isnot(None)
        )
        
        result = query.first()
        total_sessions = result.total_sessions or 0
        total_duration = result.total_duration or 0.0
        
        return StudyStats(
            total_sessions=total_sessions,
            total_duration=total_duration,
            average_session_duration=total_duration / total_sessions if total_sessions > 0 else 0.0,
            last_session=result.last_session
        )

study = CRUDStudy(StudySession)
