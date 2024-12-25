from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel

class QuestionBase(BaseModel):
    question: str
    options: List[str]
    correct_answer: str

class QuizBase(BaseModel):
    questions: List[QuestionBase]

class QuizCreate(QuizBase):
    recording_id: int

class QuizUpdate(BaseModel):
    user_answers: Dict[str, str]  # Question ID to answer mapping

class QuizInDBBase(QuizBase):
    id: int
    recording_id: int
    user_id: int
    score: Optional[float] = None
    user_answers: Optional[Dict[str, str]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Quiz(QuizInDBBase):
    pass

class QuizResult(BaseModel):
    quiz_id: int
    score: float
    correct_answers: int
    total_questions: int
    completed_at: datetime
