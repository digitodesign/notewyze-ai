from typing import List, Optional
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.quiz import Quiz
from app.schemas.quiz import QuizCreate, QuizUpdate, QuizResult
from app.core.ai import generate_quiz_questions

class CRUDQuiz(CRUDBase[Quiz, QuizCreate, QuizUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: QuizCreate, owner_id: int
    ) -> Quiz:
        # Get recording transcript
        from app.models.recording import Recording
        recording = db.query(Recording).filter(Recording.id == obj_in.recording_id).first()
        if not recording or not recording.transcript:
            raise ValueError("Recording not found or transcript not available")
        
        # Generate quiz questions using Gemini
        questions = generate_quiz_questions(recording.transcript)
        
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["questions"] = questions
        
        db_obj = self.model(**obj_in_data, user_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_recording(
        self, db: Session, *, recording_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Quiz]:
        return (
            db.query(self.model)
            .filter(Quiz.recording_id == recording_id, Quiz.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def submit_answers(
        self, db: Session, *, quiz: Quiz, answers: QuizUpdate
    ) -> QuizResult:
        # Calculate score
        correct_answers = 0
        total_questions = len(quiz.questions)
        
        for question in quiz.questions:
            question_id = str(question["id"])
            if (
                question_id in answers.user_answers
                and answers.user_answers[question_id].lower() == question["correct_answer"].lower()
            ):
                correct_answers += 1
        
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Update quiz with answers and score
        quiz.user_answers = answers.user_answers
        quiz.score = score
        quiz.completed_at = datetime.utcnow()
        
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        
        return QuizResult(
            quiz_id=quiz.id,
            score=score,
            correct_answers=correct_answers,
            total_questions=total_questions,
            completed_at=quiz.completed_at
        )

quiz = CRUDQuiz(Quiz)
