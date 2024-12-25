from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base_class import Base

class DifficultyLevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class ReadStatus(str, enum.Enum):
    unread = "unread"
    reading = "reading"
    completed = "completed"

class ResearchRecommendation(Base):
    __tablename__ = "research_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id"))
    title = Column(String)
    description = Column(Text)
    url = Column(String)
    difficulty = Column(Enum(DifficultyLevel))
    key_takeaways = Column(JSON)  # Array of strings
    relevance = Column(Integer)  # 1-10 scale
    publication_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    recording = relationship("Recording", back_populates="research_recommendations")
    saved_papers = relationship("SavedPaper", back_populates="recommendation", cascade="all, delete-orphan")

class SavedPaper(Base):
    __tablename__ = "saved_papers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recommendation_id = Column(Integer, ForeignKey("research_recommendations.id"))
    read_status = Column(Enum(ReadStatus), default=ReadStatus.unread)
    reading_progress = Column(Integer)  # 0-100 percentage
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    recommendation = relationship("ResearchRecommendation", back_populates="saved_papers")
    user = relationship("User", back_populates="saved_papers")
