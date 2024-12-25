# NoteWyze AI Project Structure

## Overview
NoteWyze AI is structured as a monorepo containing both the frontend (React Native/Expo) and backend (FastAPI) applications.

## Root Structure
```
NoteWyze AI/
├── backend/           # FastAPI backend application
├── notewyze-ai/       # React Native frontend application
├── .env              # Root environment variables
├── .env.example      # Example environment file
├── .gitignore       # Git ignore rules
├── PROGRESS.md      # Project progress tracking
└── PROJECT_STRUCTURE.md  # This file
```

## Backend Structure
```
backend/
├── app/
│   ├── api/              # API utilities
│   ├── core/             # Core functionality
│   │   ├── config.py     # Settings and configuration
│   │   ├── deps.py       # Dependencies
│   │   ├── security.py   # Security utilities
│   │   ├── auth.py       # Authentication
│   │   └── jwt_utils.py  # JWT handling
│   ├── crud/             # Database operations
│   │   ├── crud_quiz.py
│   │   ├── crud_recording.py
│   │   ├── crud_research.py
│   │   ├── crud_study.py
│   │   └── crud_user.py
│   ├── db/               # Database setup
│   │   ├── base.py       # Model imports for Alembic
│   │   ├── base_class.py # SQLAlchemy base class
│   │   ├── database.py   # Database connection
│   │   └── session.py    # Session management
│   ├── models/           # SQLAlchemy models
│   │   ├── base.py
│   │   ├── quiz.py
│   │   ├── recording.py
│   │   ├── research.py
│   │   ├── study.py
│   │   └── user.py
│   ├── routers/          # API endpoints
│   │   ├── auth.py
│   │   ├── quizzes.py
│   │   ├── recordings.py
│   │   ├── research.py
│   │   ├── study.py
│   │   └── users.py
│   ├── schemas/          # Pydantic models
│   │   ├── quiz.py
│   │   ├── recording.py
│   │   ├── research.py
│   │   ├── study.py
│   │   ├── token.py
│   │   └── user.py
│   └── utils/            # Utility functions
│       ├── ai.py         # AI/ML utilities
│       ├── audio.py      # Audio processing
│       ├── quiz.py       # Quiz generation
│       └── storage.py    # File storage
├── alembic/              # Database migrations
│   ├── versions/         # Migration versions
│   └── env.py           # Alembic environment
├── tests/                # Test files
│   ├── conftest.py      # Test configuration
│   └── test_*.py        # Test modules
├── uploads/              # File uploads directory
├── .env                 # Environment variables
├── .env.example         # Example environment file
├── alembic.ini         # Alembic configuration
├── requirements.txt    # Python dependencies
└── start.bat          # Startup script

## Frontend Structure
```
notewyze-ai/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── common/      # Shared components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Card.tsx
│   │   ├── OnboardingButton.tsx
│   │   ├── RecordingAnimation.tsx
│   │   └── WaveformButton.tsx
│   ├── contexts/        # React contexts
│   │   ├── AuthContext.tsx
│   │   └── ThemeContext.tsx
│   ├── database/        # Local database
│   │   └── schema.ts
│   ├── navigation/      # Navigation
│   │   └── AppNavigator.tsx
│   ├── screens/         # App screens
│   │   ├── onboarding/
│   │   │   ├── Welcome.tsx
│   │   │   ├── Features.tsx
│   │   │   └── Setup.tsx
│   │   ├── HomeScreen.tsx
│   │   ├── LibraryScreen.tsx
│   │   ├── LoginScreen.tsx
│   │   ├── ProfileScreen.tsx
│   │   ├── ProgressScreen.tsx
│   │   ├── QuizScreen.tsx
│   │   ├── RecordScreen.tsx
│   │   ├── RegisterScreen.tsx
│   │   ├── ResearchScreen.tsx
│   │   └── ReviewScreen.tsx
│   ├── services/        # API services
│   │   ├── aiService.ts
│   │   ├── api.ts
│   │   ├── audioService.ts
│   │   └── authService.ts
│   ├── theme/          # Styling
│   │   └── index.ts
│   ├── types/          # TypeScript types
│   │   └── index.ts
│   └── utils/          # Utilities
│       └── helpers.ts
├── assets/             # Static assets
│   ├── fonts/
│   └── images/
├── App.tsx            # Root component
├── app.json          # Expo config
├── babel.config.js   # Babel config
├── package.json      # Dependencies
└── tsconfig.json    # TypeScript config
```

## Key Files and Their Purposes

### Backend

#### Core Files
- `app/core/config.py`: Application configuration and environment variables
- `app/core/security.py`: Security utilities including password hashing and JWT
- `app/core/deps.py`: Dependency injection and shared dependencies

#### Database
- `app/db/base.py`: SQLAlchemy model imports for Alembic
- `app/db/session.py`: Database session management
- `alembic/env.py`: Database migration environment

#### API and Routes
- `app/routers/*.py`: API endpoint definitions
- `app/schemas/*.py`: Request/Response models
- `app/crud/*.py`: Database operations

#### Utilities
- `app/utils/ai.py`: AI integration with Google Gemini
- `app/utils/audio.py`: Audio processing utilities
- `app/utils/storage.py`: File storage management

### Frontend

#### Core Files
- `App.tsx`: Application entry point
- `src/navigation/AppNavigator.tsx`: Navigation configuration
- `src/contexts/*.tsx`: Global state management

#### Features
- `src/screens/*.tsx`: Main application screens
- `src/components/*.tsx`: Reusable UI components
- `src/services/*.ts`: API integration services

#### Configuration
- `app.json`: Expo configuration
- `tsconfig.json`: TypeScript configuration
- `package.json`: Dependencies and scripts

## File Naming Conventions

### Backend
- Models: Singular noun (e.g., `user.py`, `recording.py`)
- Routers: Plural noun (e.g., `users.py`, `recordings.py`)
- CRUD: Prefix with `crud_` (e.g., `crud_user.py`)
- Schemas: Singular noun (e.g., `user.py`, `recording.py`)

### Frontend
- Components: PascalCase (e.g., `Button.tsx`, `RecordingCard.tsx`)
- Screens: Suffix with Screen (e.g., `HomeScreen.tsx`)
- Services: Suffix with Service (e.g., `authService.ts`)
- Utils: Camel case (e.g., `helpers.ts`, `formatters.ts`)

## Important Notes
1. All environment variables should be documented in `.env.example`
2. Test files should mirror the structure of the code they test
3. Keep components small and focused on a single responsibility
4. Use TypeScript interfaces for all data structures
5. Follow consistent naming conventions across the project
