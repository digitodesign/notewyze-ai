from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Enum, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class DifficultyLevel(enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    recordings = relationship("Recording", back_populates="user")
    quizzes = relationship("Quiz", back_populates="user")
    saved_papers = relationship("SavedPaper", back_populates="user")
    study_sessions = relationship("StudySession", back_populates="user")

class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    audio_url = Column(String)
    transcript = Column(String)
    duration = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="recordings")
    quizzes = relationship("Quiz", back_populates="recording")
    research_recommendations = relationship("ResearchRecommendation", back_populates="recording")

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Float)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recording = relationship("Recording", back_populates="quizzes")
    user = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")
    study_sessions = relationship("StudySession", back_populates="quiz")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    question_text = Column(String)
    options = Column(JSON)  # Array of strings
    correct_answer = Column(String)
    explanation = Column(String)
    topic_area = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    quiz = relationship("Quiz", back_populates="questions")
    research_relevance = relationship("ResearchRelevance", back_populates="question")

class ResearchRecommendation(Base):
    __tablename__ = "research_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id"))
    title = Column(String)
    description = Column(String)
    relevance = Column(String)
    difficulty = Column(Enum(DifficultyLevel))
    key_takeaways = Column(JSON)  # Array of strings
    url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recording = relationship("Recording", back_populates="research_recommendations")
    research_relevance = relationship("ResearchRelevance", back_populates="recommendation")
    saved_papers = relationship("SavedPaper", back_populates="recommendation")

class ResearchRelevance(Base):
    __tablename__ = "research_relevance"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("research_recommendations.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    topic_overlap = Column(String)
    relevance_score = Column(Float)  # 0-1 score of how relevant the paper is to the question
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recommendation = relationship("ResearchRecommendation", back_populates="research_relevance")
    question = relationship("Question", back_populates="research_relevance")

class SavedPaper(Base):
    __tablename__ = "saved_papers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recommendation_id = Column(Integer, ForeignKey("research_recommendations.id"))
    read_status = Column(Boolean, default=False)
    reading_progress = Column(Float, default=0)  # 0-1 progress through the paper
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="saved_papers")
    recommendation = relationship("ResearchRecommendation", back_populates="saved_papers")
    study_sessions = relationship("StudySession", back_populates="saved_paper")

class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    saved_paper_id = Column(Integer, ForeignKey("saved_papers.id"))
    notes = Column(String)
    duration = Column(Integer)  # Duration in minutes
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="study_sessions")
    quiz = relationship("Quiz", back_populates="study_sessions")
    saved_paper = relationship("SavedPaper", back_populates="study_sessions")
