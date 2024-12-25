from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.recording import Recording
from app.schemas.recording import RecordingCreate, RecordingUpdate, RecordingWithProgress
from app.core.audio import process_audio_file, extract_transcript
from app.core.ai import generate_summary

class CRUDRecording(CRUDBase[Recording, RecordingCreate, RecordingUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: RecordingCreate, owner_id: int, audio_file: bytes
    ) -> Recording:
        obj_in_data = jsonable_encoder(obj_in)
        
        # Process audio file and get duration
        file_path, duration = process_audio_file(audio_file)
        obj_in_data["file_path"] = file_path
        obj_in_data["duration"] = duration
        
        # Extract transcript using speech-to-text
        transcript = extract_transcript(file_path)
        obj_in_data["transcript"] = transcript
        
        # Generate summary using Gemini
        summary = generate_summary(transcript)
        obj_in_data["summary"] = summary
        
        db_obj = self.model(**obj_in_data, user_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[RecordingWithProgress]:
        recordings = (
            db.query(self.model)
            .filter(Recording.user_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # Enhance recordings with progress information
        enhanced_recordings = []
        for recording in recordings:
            quiz_stats = self._get_quiz_stats(db, recording.id)
            study_stats = self._get_study_stats(db, recording.id)
            research_count = self._get_research_count(db, recording.id)
            
            enhanced_recording = RecordingWithProgress(
                **jsonable_encoder(recording),
                quiz_count=quiz_stats["count"],
                average_quiz_score=quiz_stats["average_score"],
                study_time=study_stats["total_duration"],
                research_count=research_count
            )
            enhanced_recordings.append(enhanced_recording)
        
        return enhanced_recordings

    def _get_quiz_stats(self, db: Session, recording_id: int) -> dict:
        from app.models.quiz import Quiz
        quizzes = db.query(Quiz).filter(Quiz.recording_id == recording_id).all()
        if not quizzes:
            return {"count": 0, "average_score": None}
        
        completed_quizzes = [q for q in quizzes if q.score is not None]
        if not completed_quizzes:
            return {"count": len(quizzes), "average_score": None}
        
        avg_score = sum(q.score for q in completed_quizzes) / len(completed_quizzes)
        return {"count": len(quizzes), "average_score": avg_score}

    def _get_study_stats(self, db: Session, recording_id: int) -> dict:
        from app.models.study import StudySession
        sessions = db.query(StudySession).filter(
            StudySession.recording_id == recording_id,
            StudySession.duration.isnot(None)
        ).all()
        
        total_duration = sum(session.duration for session in sessions)
        return {"total_duration": total_duration}

    def _get_research_count(self, db: Session, recording_id: int) -> int:
        from app.models.research import ResearchRecommendation
        return db.query(ResearchRecommendation).filter(
            ResearchRecommendation.recording_id == recording_id
        ).count()

recording = CRUDRecording(Recording)
