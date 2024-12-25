from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class StudySessionBase(BaseModel):
    notes: Optional[str] = None

class StudySessionCreate(StudySessionBase):
    recording_id: int

class StudySessionUpdate(StudySessionBase):
    end_time: datetime

class StudySessionInDBBase(StudySessionBase):
    id: int
    recording_id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None  # Duration in minutes

    class Config:
        from_attributes = True

class StudySession(StudySessionInDBBase):
    pass

class StudyStats(BaseModel):
    total_sessions: int
    total_duration: float  # Total duration in minutes
    average_session_duration: float  # Average duration in minutes
    last_session: Optional[datetime] = None
