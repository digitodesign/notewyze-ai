from typing import List, Optional
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.research import ResearchRecommendation, SavedPaper
from app.schemas.research import (
    ResearchRecommendationCreate,
    SavedPaperCreate,
    SavedPaperUpdate
)
from app.core.ai import generate_research_recommendations

class CRUDResearch:
    def generate_recommendations(
        self, db: Session, *, recording_id: int, user_id: int
    ) -> List[ResearchRecommendation]:
        # Get recording transcript
        from app.models.recording import Recording
        recording = db.query(Recording).filter(Recording.id == recording_id).first()
        if not recording or not recording.transcript:
            raise ValueError("Recording not found or transcript not available")
        
        # Generate recommendations using Gemini
        recommendations = generate_research_recommendations(recording.transcript)
        
        # Save recommendations to database
        db_recommendations = []
        for rec in recommendations:
            db_rec = ResearchRecommendation(
                **rec,
                recording_id=recording_id,
                user_id=user_id
            )
            db.add(db_rec)
            db_recommendations.append(db_rec)
        
        db.commit()
        for rec in db_recommendations:
            db.refresh(rec)
        
        return db_recommendations

    def get_recommendations_by_recording(
        self, db: Session, *, recording_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ResearchRecommendation]:
        return (
            db.query(ResearchRecommendation)
            .filter(
                ResearchRecommendation.recording_id == recording_id,
                ResearchRecommendation.user_id == user_id
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def save_paper(
        self, db: Session, *, obj_in: SavedPaperCreate, user_id: int
    ) -> SavedPaper:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = SavedPaper(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_saved_papers(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[SavedPaper]:
        return (
            db.query(SavedPaper)
            .filter(SavedPaper.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_saved_paper(
        self, db: Session, *, id: int
    ) -> Optional[SavedPaper]:
        return db.query(SavedPaper).filter(SavedPaper.id == id).first()

    def update_saved_paper(
        self, db: Session, *, db_obj: SavedPaper, obj_in: SavedPaperUpdate
    ) -> SavedPaper:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        
        if update_data.get("read_status") or update_data.get("reading_progress"):
            update_data["last_read_at"] = datetime.utcnow()
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_saved_paper(
        self, db: Session, *, id: int
    ) -> None:
        obj = db.query(SavedPaper).get(id)
        db.delete(obj)
        db.commit()

research = CRUDResearch()
