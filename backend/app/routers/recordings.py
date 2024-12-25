from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.api.errors import NotFoundError, ValidationError
from app.api.responses import create_success_response
from app.api.pagination import PaginationParams, paginate_query
from app.crud.crud_recording import recording as crud_recording
from app.models.user import User
from app.schemas.recording import RecordingCreate, RecordingUpdate, Recording
from app.utils.audio import process_audio_file
from app.utils.storage import save_file

router = APIRouter()

@router.get("/", response_model=dict)
def get_recordings(
    params: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get paginated recordings for the current user.
    """
    query = crud_recording.get_multi_by_user(db, user_id=current_user.id)
    return create_success_response(
        data=paginate_query(query, params),
        message="Recordings retrieved successfully",
    )

@router.post("/", response_model=dict)
async def create_recording(
    title: str,
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new recording with audio file.
    """
    # Validate file type
    if not audio_file.content_type.startswith('audio/'):
        raise ValidationError(
            detail="Invalid file type. Only audio files are allowed.",
            code="INVALID_FILE_TYPE"
        )
    
    # Save audio file
    file_path = await save_file(audio_file, "recordings")
    
    # Process audio file (transcription, etc.)
    audio_data = await process_audio_file(file_path)
    
    # Create recording
    recording_data = RecordingCreate(
        title=title,
        file_path=file_path,
        duration=audio_data.duration,
        transcription=audio_data.transcription,
    )
    recording = crud_recording.create_with_user(
        db=db,
        obj_in=recording_data,
        user_id=current_user.id,
    )
    
    return create_success_response(
        data=recording,
        message="Recording created successfully",
    )

@router.get("/{recording_id}", response_model=dict)
def get_recording(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific recording by ID.
    """
    recording = crud_recording.get(db=db, id=recording_id)
    if not recording or recording.user_id != current_user.id:
        raise NotFoundError(detail="Recording not found")
    
    return create_success_response(
        data=recording,
        message="Recording retrieved successfully",
    )

@router.put("/{recording_id}", response_model=dict)
def update_recording(
    recording_id: int,
    recording_in: RecordingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a recording.
    """
    recording = crud_recording.get(db=db, id=recording_id)
    if not recording or recording.user_id != current_user.id:
        raise NotFoundError(detail="Recording not found")
    
    recording = crud_recording.update(
        db=db,
        db_obj=recording,
        obj_in=recording_in,
    )
    return create_success_response(
        data=recording,
        message="Recording updated successfully",
    )

@router.delete("/{recording_id}", response_model=dict)
def delete_recording(
    recording_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a recording.
    """
    recording = crud_recording.get(db=db, id=recording_id)
    if not recording or recording.user_id != current_user.id:
        raise NotFoundError(detail="Recording not found")
    
    crud_recording.remove(db=db, id=recording_id)
    return create_success_response(
        message="Recording deleted successfully",
    )
