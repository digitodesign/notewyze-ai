from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class RecordingBase(BaseModel):
    title: str
    description: Optional[str] = None

class RecordingCreate(RecordingBase):
    file_path: str
    duration: float

class RecordingUpdate(RecordingBase):
    transcript: Optional[str] = None
    summary: Optional[str] = None

class RecordingInDBBase(RecordingBase):
    id: int
    file_path: str
    duration: float
    transcript: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        from_attributes = True

class Recording(RecordingInDBBase):
    pass

class RecordingWithProgress(Recording):
    quiz_count: int
    average_quiz_score: Optional[float] = None
    study_time: float  # Total study time in minutes
    research_count: int
