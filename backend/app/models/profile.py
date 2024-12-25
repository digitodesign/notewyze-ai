from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    study_preferences = Column(JSON, default={
        "preferred_duration": 30,  # minutes
        "difficulty_level": "intermediate",
        "topics_of_interest": []
    })
    statistics = Column(JSON, default={
        "total_study_time": 0,  # minutes
        "completed_quizzes": 0,
        "average_score": 0
    })
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="profile")
