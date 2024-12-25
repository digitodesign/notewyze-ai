from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.api.errors import NotFoundError
from app.api.responses import create_success_response
from app.api.pagination import PaginationParams, paginate_query
from app.crud.crud_quiz import quiz as crud_quiz
from app.models.user import User
from app.schemas.quiz import QuizCreate, QuizUpdate, Quiz
from app.utils.quiz import generate_quiz_questions

router = APIRouter()

@router.get("/", response_model=dict)
def get_quizzes(
    params: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get paginated quizzes for the current user.
    """
    query = crud_quiz.get_multi_by_user(db, user_id=current_user.id)
    return create_success_response(
        data=paginate_query(query, params),
        message="Quizzes retrieved successfully",
    )

@router.post("/generate/{recording_id}", response_model=dict)
async def generate_quiz(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate a new quiz for a recording.
    """
    # First check if recording exists and belongs to user
    recording = crud_quiz.get_recording(db, recording_id=recording_id)
    if not recording or recording.user_id != current_user.id:
        raise NotFoundError(detail="Recording not found")

    # Generate quiz questions using AI
    questions = await generate_quiz_questions(recording.transcript)
    
    # Create quiz
    quiz_data = QuizCreate(
        recording_id=recording_id,
        questions=questions,
    )
    quiz = crud_quiz.create_with_user(
        db=db,
        obj_in=quiz_data,
        user_id=current_user.id,
    )
    
    return create_success_response(
        data=quiz,
        message="Quiz generated successfully",
    )

@router.get("/{quiz_id}", response_model=dict)
def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific quiz by ID.
    """
    quiz = crud_quiz.get(db=db, id=quiz_id)
    if not quiz or quiz.user_id != current_user.id:
        raise NotFoundError(detail="Quiz not found")
    
    return create_success_response(
        data=quiz,
        message="Quiz retrieved successfully",
    )

@router.post("/{quiz_id}/submit", response_model=dict)
def submit_quiz(
    quiz_id: int,
    answers: dict[int, str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Submit answers for a quiz and get results.
    """
    quiz = crud_quiz.get(db=db, id=quiz_id)
    if not quiz or quiz.user_id != current_user.id:
        raise NotFoundError(detail="Quiz not found")
    
    # Calculate score and update quiz
    score = crud_quiz.calculate_score(quiz, answers)
    quiz_update = QuizUpdate(
        completed=True,
        score=score,
        submitted_answers=answers,
    )
    quiz = crud_quiz.update(
        db=db,
        db_obj=quiz,
        obj_in=quiz_update,
    )
    
    return create_success_response(
        data={
            "quiz": quiz,
            "score": score,
            "feedback": crud_quiz.generate_feedback(quiz, answers),
        },
        message="Quiz submitted successfully",
    )

@router.delete("/{quiz_id}", response_model=dict)
def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a quiz.
    """
    quiz = crud_quiz.get(db=db, id=quiz_id)
    if not quiz or quiz.user_id != current_user.id:
        raise NotFoundError(detail="Quiz not found")
    
    crud_quiz.remove(db=db, id=quiz_id)
    return create_success_response(
        message="Quiz deleted successfully",
    )
