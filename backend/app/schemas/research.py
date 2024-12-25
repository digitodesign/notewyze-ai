from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl

class ResearchRecommendationBase(BaseModel):
    title: str
    authors: str
    abstract: str
    url: HttpUrl
    relevance_score: float

class ResearchRecommendationCreate(ResearchRecommendationBase):
    recording_id: int

class ResearchRecommendationInDBBase(ResearchRecommendationBase):
    id: int
    recording_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ResearchRecommendation(ResearchRecommendationInDBBase):
    pass

class SavedPaperBase(BaseModel):
    read_status: bool = False
    reading_progress: float = 0.0
    notes: Optional[str] = None

class SavedPaperCreate(SavedPaperBase):
    recommendation_id: int

class SavedPaperUpdate(SavedPaperBase):
    pass

class SavedPaperInDBBase(SavedPaperBase):
    id: int
    recommendation_id: int
    user_id: int
    saved_at: datetime
    last_read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SavedPaper(SavedPaperInDBBase):
    recommendation: ResearchRecommendation
