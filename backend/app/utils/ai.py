import google.generativeai as genai
from app.core.config import settings
from typing import List, Dict, Any

# Configure the Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def generate_quiz(transcript: str, num_questions: int = 5) -> List[Dict[str, Any]]:
    """
    Generate a quiz based on the lecture transcript.
    Returns a list of questions with their answers.
    """
    prompt = f"""
    Based on the following lecture transcript, generate {num_questions} multiple-choice questions.
    Format each question as a JSON object with the following structure:
    {{
        "question": "The question text",
        "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
        "correct_answer": "The correct option letter (A, B, C, or D)",
        "explanation": "Explanation of why this is the correct answer"
    }}
    
    Transcript:
    {transcript}
    """
    
    response = model.generate_content(prompt)
    # Process and validate the response
    try:
        questions = eval(response.text)  # Convert string representation to Python objects
        return questions
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return []

def generate_research_recommendations(transcript: str, num_recommendations: int = 5) -> List[Dict[str, str]]:
    """
    Generate research paper recommendations based on the lecture content.
    """
    prompt = f"""
    Based on the following lecture transcript, suggest {num_recommendations} research papers or academic resources
    that would be valuable for further study. Format each recommendation as a JSON object with title, authors,
    brief description, and relevance to the lecture content.
    
    Transcript:
    {transcript}
    """
    
    response = model.generate_content(prompt)
    try:
        recommendations = eval(response.text)
        return recommendations
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return []

def generate_study_notes(transcript: str) -> Dict[str, Any]:
    """
    Generate structured study notes from the lecture transcript.
    """
    prompt = f"""
    Create organized study notes from this lecture transcript. Include:
    1. Main topics and subtopics
    2. Key concepts and definitions
    3. Important examples
    4. Summary points
    
    Format the response as a structured JSON object.
    
    Transcript:
    {transcript}
    """
    
    response = model.generate_content(prompt)
    try:
        study_notes = eval(response.text)
        return study_notes
    except Exception as e:
        print(f"Error generating study notes: {e}")
        return {}
