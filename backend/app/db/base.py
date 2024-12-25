# Import all the models here for Alembic autogenerate support
from app.db.base_class import Base
from app.models.user import User
from app.models.recording import Recording
from app.models.quiz import Quiz, QuizQuestion
from app.models.study import StudySession
from app.models.research import ResearchRecommendation, SavedPaper
from app.models.profile import Profile
