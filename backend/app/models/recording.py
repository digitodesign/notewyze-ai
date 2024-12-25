from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    duration = Column(String)  # Duration in format "HH:MM:SS"
    summary = Column(Text, nullable=True)
    transcription = Column(Text, nullable=True)
    file_path = Column(String)  # Internal use only, not exposed to frontend
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="recordings")
    quizzes = relationship("Quiz", back_populates="recording", cascade="all, delete-orphan")
    research_recommendations = relationship("ResearchRecommendation", back_populates="recording", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="recording", cascade="all, delete-orphan")
