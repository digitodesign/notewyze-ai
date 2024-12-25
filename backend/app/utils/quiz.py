import google.generativeai as genai
from typing import List, Dict
import json
import logging
import os
from dotenv import load_dotenv
from models import Quiz, Question
from google.api_core import exceptions as google_exceptions

load_dotenv()

# Configure Gemini API
if 'GEMINI_API_KEY' not in os.environ:
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

logger = logging.getLogger(__name__)

QUIZ_GENERATION_PROMPT = """
You are an expert educator. Given the following lecture transcript, create a comprehensive multiple-choice quiz to test understanding of the key concepts.

Rules for quiz generation:
1. Create 5 multiple-choice questions that test different aspects and difficulty levels
2. Each question MUST have EXACTLY 4 options labeled A, B, C, and D
3. Include a brief explanation for why the correct answer is right
4. Make questions engaging and thought-provoking
5. Focus on testing understanding rather than mere recall
6. DO NOT create true/false questions
7. Each question must have exactly 4 distinct answer choices

Return the quiz in the following JSON format:
{
    "title": "Quiz title based on content",
    "questions": [
        {
            "question": "Question text?",
            "options": [
                "A) First option",
                "B) Second option",
                "C) Third option",
                "D) Fourth option"
            ],
            "correct_answer": "The exact text of the correct option",
            "explanation": "Why this answer is correct"
        }
    ]
}

Example question:
{
    "question": "What is the primary advantage of Python's high-level nature?",
    "options": [
        "A) It makes the code run faster",
        "B) It improves code readability and simplicity",
        "C) It requires less memory",
        "D) It automatically fixes bugs"
    ],
    "correct_answer": "B) It improves code readability and simplicity",
    "explanation": "Python's high-level nature abstracts away complex implementation details, making code more readable and easier to write and maintain."
}

Lecture transcript:
"""

def generate_quiz(transcript: str) -> Dict:
    """
    Generate a quiz from the given transcript using Gemini API.
    Returns a dictionary containing the quiz data.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = QUIZ_GENERATION_PROMPT + transcript

        response = model.generate_content(prompt)
        
        # Extract JSON from response
        try:
            quiz_data = json.loads(response.text)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from API: {response.text}")
            raise ValueError("API response was not in valid JSON format")
        
        # Validate quiz format
        if not all(key in quiz_data for key in ['title', 'questions']):
            logger.error(f"Missing required fields in quiz data: {quiz_data}")
            raise ValueError("Invalid quiz format from API: missing required fields")
            
        # Validate each question has required fields
        for i, question in enumerate(quiz_data['questions']):
            if not all(key in question for key in ['question', 'options', 'correct_answer', 'explanation']):
                logger.error(f"Invalid question format in question {i}: {question}")
                raise ValueError(f"Invalid question format from API: missing required fields in question {i}")
            if len(question['options']) != 4:
                logger.error(f"Wrong number of options in question {i}: {question}")
                raise ValueError(f"Each question must have exactly 4 options (question {i} has {len(question['options'])})")
                
            # Validate that correct_answer is one of the options
            if question['correct_answer'] not in question['options']:
                logger.error(f"Correct answer not in options for question {i}: {question}")
                raise ValueError(f"Correct answer must be one of the options (question {i})")
                
        return quiz_data
        
    except google_exceptions.InvalidArgument as e:
        logger.error(f"Invalid argument error: {str(e)}")
        raise ValueError(f"Invalid argument to Gemini API: {str(e)}")
    except genai.exceptions.APIError as e:
        logger.error(f"API error generating quiz: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        raise

def create_quiz_in_db(db_session, recording_id: int, quiz_data: Dict) -> Quiz:
    """
    Create a quiz and its questions in the database.
    Returns the created Quiz object.
    """
    try:
        # Create quiz
        quiz = Quiz(
            title=quiz_data['title'],
            recording_id=recording_id
        )
        db_session.add(quiz)
        db_session.flush()  # Get quiz ID
        
        # Create questions
        for q_data in quiz_data['questions']:
            question = Question(
                quiz_id=quiz.id,
                question_text=q_data['question'],
                options=q_data['options'],
                correct_answer=q_data['correct_answer'],
                explanation=q_data['explanation']
            )
            db_session.add(question)
            
        db_session.commit()
        return quiz
        
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error creating quiz in database: {str(e)}")
        raise
