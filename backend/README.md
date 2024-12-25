# NoteWyze AI Backend

This is the FastAPI backend for NoteWyze AI, a lecture companion app that records lectures, transcribes them, generates quizzes, and provides research recommendations using AI.

## Project Structure
```
backend/
├── alembic/            # Database migrations
├── app/                # Main application code
│   ├── api/           # API endpoints
│   ├── core/          # Core functionality (config, security)
│   ├── crud/          # Database operations
│   ├── db/            # Database setup and session
│   ├── models/        # SQLAlchemy models
│   ├── routers/       # API routes
│   └── schemas/       # Pydantic models
├── tests/             # Test files
└── requirements.txt   # Python dependencies
```

## Setup and Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
- Copy `.env.example` to `.env`
- Fill in the required values

5. Run migrations:
```bash
alembic upgrade head
```

6. Start the server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
