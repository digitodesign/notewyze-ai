import os
os.environ["TESTING"] = "true"

import pytest
import pytest_asyncio
import google.generativeai as genai
import json
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
from datetime import datetime
import sys
import re

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.research import generate_research_prompt, router
from database import get_db, Base, engine
from models import Recording, Quiz, Question, ResearchRecommendation, User
from tests.mock_auth import get_current_user

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# Create a FastAPI test app
from fastapi import FastAPI, Depends
app = FastAPI()

# Override auth dependency
app.dependency_overrides[get_current_user] = get_current_user

# Include research router
app.include_router(router, prefix="/research")

# Sample transcript for testing
SAMPLE_TRANSCRIPT = """
In today's lecture on Machine Learning, we covered supervised learning algorithms.
Key concepts included:
1. Linear Regression
2. Decision Trees
3. Support Vector Machines
We discussed how these algorithms learn from labeled data and make predictions.
The importance of feature selection and model evaluation was emphasized.
"""

SAMPLE_QUIZ_RESULTS = {
    "score": 75,
    "weak_topics": ["Support Vector Machines", "Model Evaluation"],
    "strong_topics": ["Linear Regression"]
}

# Create test database session
from sqlalchemy.orm import sessionmaker
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_client():
    """Create a test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def db():
    """Create a test database session."""
    async with async_session() as session:
        yield session

@pytest_asyncio.fixture(autouse=True)
async def setup_database(db):
    # Create tables
    async with db.begin():
        await db.run_sync(Base.metadata.drop_all)
        await db.run_sync(Base.metadata.create_all)
    
    # Create test user
    test_user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="test_hash"
    )
    db.add(test_user)
    await db.commit()
    
    yield
    
    # Cleanup
    async with db.begin():
        await db.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_prompt_generation():
    # Test prompt generation without quiz results
    basic_prompt = await generate_research_prompt(SAMPLE_TRANSCRIPT)
    assert "Based on this lecture transcript" in basic_prompt
    assert SAMPLE_TRANSCRIPT in basic_prompt
    assert "Format the response as a JSON array" in basic_prompt

    # Test prompt generation with quiz results
    quiz_prompt = await generate_research_prompt(SAMPLE_TRANSCRIPT, SAMPLE_QUIZ_RESULTS)
    assert "Quiz Performance" in quiz_prompt
    assert "Support Vector Machines" in quiz_prompt
    assert "Linear Regression" in quiz_prompt

@pytest.mark.asyncio
async def test_gemini_response_format():
    # Initialize Gemini (make sure GEMINI_API_KEY is set in environment)
    prompt = await generate_research_prompt(SAMPLE_TRANSCRIPT, SAMPLE_QUIZ_RESULTS)
    response = model.generate_content(prompt)
    
    try:
        # Extract JSON from markdown code block if present
        text = response.text
        json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        
        # Parse response as JSON
        recommendations = json.loads(text)
        
        # Verify structure
        assert "recommendations" in recommendations
        assert isinstance(recommendations["recommendations"], list)
        assert len(recommendations["recommendations"]) > 0
        
        # Check first recommendation
        first_rec = recommendations["recommendations"][0]
        required_fields = [
            "title", "description", "relevance", "difficulty",
            "keyTakeaways", "url"
        ]
        for field in required_fields:
            assert field in first_rec
            
        # Verify difficulty is valid
        assert first_rec["difficulty"] in ["beginner", "intermediate", "advanced"]
        
        # Verify keyTakeaways is a list
        assert isinstance(first_rec["keyTakeaways"], list)
        assert len(first_rec["keyTakeaways"]) >= 3
        
        # If quiz results provided, check topicOverlap
        if SAMPLE_QUIZ_RESULTS:
            assert "topicOverlap" in first_rec
            
    except json.JSONDecodeError:
        pytest.fail("Gemini response is not valid JSON")
    except AssertionError as e:
        pytest.fail(f"Response format incorrect: {str(e)}")

@pytest.mark.asyncio
async def test_recommendation_generation_endpoint(test_client, db):
    """Test generating research recommendations for a recording"""
    try:
        async with db.begin():
            # Get test user
            result = await db.execute(select(User).where(User.email == "test@example.com"))
            user = result.scalar_one()
            
            # Create test recording
            recording = Recording(
                title="Test ML Lecture",
                transcript=SAMPLE_TRANSCRIPT,
                user_id=user.id
            )
            db.add(recording)
            await db.flush()  # Get the ID without committing
            
            # Create test quiz
            quiz = Quiz(
                recording_id=recording.id,
                user_id=user.id,
                score=75.0,
                completed_at=datetime.now()
            )
            db.add(quiz)
            await db.flush()
            
            # Add questions
            questions = [
                Question(
                    quiz_id=quiz.id,
                    question_text="What is Linear Regression?",
                    options=["A", "B", "C", "D"],
                    correct_answer="A",
                    topic_area="Linear Regression"
                ),
                Question(
                    quiz_id=quiz.id,
                    question_text="Explain SVM kernels",
                    options=["A", "B", "C", "D"],
                    correct_answer="B",
                    topic_area="Support Vector Machines"
                )
            ]
            for q in questions:
                db.add(q)

            await db.commit()
            recording_id = recording.id

        # Create auth token
        headers = {"Authorization": f"Bearer test_token"}
        
        # Test endpoint
        response = await test_client.post(
            f"/research/recommendations/{recording_id}",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "recommendations" in data
        
        # Verify recommendations were saved
        async with db.begin():
            result = await db.execute(
                select(ResearchRecommendation)
                .where(ResearchRecommendation.recording_id == recording_id)
            )
            recommendations = result.scalars().all()
            assert len(recommendations) > 0
            
            # Check first recommendation
            first_rec = recommendations[0]
            assert first_rec.title
            assert first_rec.description
            assert first_rec.difficulty
            assert first_rec.key_takeaways
            assert isinstance(first_rec.key_takeaways, list)
        
    except Exception as e:
        await db.rollback()
        raise e

@pytest.mark.asyncio
async def test_error_handling(test_client, db):
    """Test error handling in research endpoints"""
    try:
        async with db.begin():
            # Get test user
            result = await db.execute(select(User).where(User.email == "test@example.com"))
            user = result.scalar_one()
            
            # Test with non-existent recording
            headers = {"Authorization": f"Bearer test_token"}
            response = await test_client.post(
                f"/research/recommendations/99999",
                headers=headers
            )
            assert response.status_code == 404
            
    except Exception as e:
        await db.rollback()
        raise e

if __name__ == "__main__":
    pytest.main([__file__])
