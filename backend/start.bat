@echo off
echo Setting up NoteWyze AI Backend...

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install/upgrade pip and dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Run migrations
alembic upgrade head

REM Start the server
echo Starting FastAPI server...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
