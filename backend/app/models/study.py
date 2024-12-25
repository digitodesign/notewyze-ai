from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)  # Duration in minutes
    notes = Column(Text, nullable=True)
    
    # Foreign Keys
    recording_id = Column(Integer, ForeignKey("recordings.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    recording = relationship("Recording", back_populates="study_sessions")
    user = relationship("User", back_populates="study_sessions")
