from .audio import process_audio_file, extract_transcript
from .security import get_password_hash, verify_password
from .config import settings
from .deps import get_db, get_current_user, get_current_active_user
from .health import get_health_status
from .jwt_utils import create_access_token, decode_access_token
from .security import verify_password_reset_token, generate_password_reset_token
from .ai import (
    generate_summary,
    generate_quiz_questions,
    analyze_study_patterns,
    generate_research_recommendations
)

__all__ = [
    'process_audio_file',
    'extract_transcript',
    'get_password_hash',
    'verify_password',
    'settings',
    'get_db',
    'get_current_user',
    'get_current_active_user',
    'get_health_status',
    'create_access_token',
    'decode_access_token',
    'verify_password_reset_token',
    'generate_password_reset_token',
    'generate_summary',
    'generate_quiz_questions',
    'analyze_study_patterns',
    'generate_research_recommendations'
]
