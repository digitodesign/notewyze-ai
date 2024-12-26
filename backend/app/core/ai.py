"""AI utilities for NoteWyze AI."""
import google.generativeai as genai
from typing import Optional, List, Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

async def generate_summary(transcript: str, max_length: Optional[int] = None) -> str:
    """
    Generate a summary of the transcript using Google's Gemini AI.
    
    Args:
        transcript: The text to summarize
        max_length: Optional maximum length for the summary
        
    Returns:
        str: The generated summary
        
    Raises:
        Exception: If there's an error generating the summary
    """
    try:
        # Create the prompt
        prompt = f"""Please provide a clear and concise summary of the following transcript. 
        Focus on the main points and key takeaways.
        
        Transcript:
        {transcript}
        
        {f'Please keep the summary under {max_length} characters.' if max_length else ''}
        """
        
        # Generate the summary
        response = model.generate_content(prompt)
        
        if not response.text:
            raise Exception("No summary generated")
            
        summary = response.text.strip()
        
        # Truncate if needed
        if max_length and len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
            
        return summary
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise Exception(f"Failed to generate summary: {str(e)}")

async def generate_quiz_questions(
    transcript: str,
    num_questions: int = 5,
    difficulty: str = "medium"
) -> List[Dict[str, Any]]:
    """
    Generate quiz questions based on the transcript using Google's Gemini AI.
    
    Args:
        transcript: The text to generate questions from
        num_questions: Number of questions to generate
        difficulty: Difficulty level of questions ('easy', 'medium', 'hard')
        
    Returns:
        List[Dict[str, Any]]: List of questions with answers
        
    Raises:
        Exception: If there's an error generating questions
    """
    try:
        # Create the prompt
        prompt = f"""Generate {num_questions} {difficulty}-level multiple choice questions based on this transcript.
        For each question, provide 4 options and indicate the correct answer.
        Format the response as a list of dictionaries, with each dictionary containing:
        - question: The question text
        - options: List of 4 possible answers
        - correct_answer: The index of the correct answer (0-3)
        - explanation: Brief explanation of why the answer is correct
        
        Transcript:
        {transcript}
        """
        
        # Generate the questions
        response = model.generate_content(prompt)
        
        if not response.text:
            raise Exception("No questions generated")
            
        # Parse and validate the response
        # Note: In a production environment, you'd want more robust parsing
        questions = eval(response.text)  # Be careful with eval in production!
        
        # Validate the structure
        for q in questions:
            if not all(key in q for key in ["question", "options", "correct_answer", "explanation"]):
                raise Exception("Invalid question format")
            if len(q["options"]) != 4:
                raise Exception("Each question must have exactly 4 options")
            if not 0 <= q["correct_answer"] <= 3:
                raise Exception("Correct answer index must be between 0 and 3")
                
        return questions
        
    except Exception as e:
        logger.error(f"Error generating quiz questions: {str(e)}")
        raise Exception(f"Failed to generate quiz questions: {str(e)}")

async def analyze_study_patterns(transcripts: List[str]) -> Dict[str, Any]:
    """
    Analyze study patterns across multiple transcripts using Google's Gemini AI.
    
    Args:
        transcripts: List of transcripts to analyze
        
    Returns:
        Dict[str, Any]: Analysis results
        
    Raises:
        Exception: If there's an error analyzing patterns
    """
    try:
        # Combine transcripts with markers
        combined = "\n---\n".join(transcripts)
        
        # Create the prompt
        prompt = f"""Analyze these study session transcripts and provide insights about:
        1. Common topics and themes
        2. Learning patterns and habits
        3. Areas of focus
        4. Potential knowledge gaps
        5. Recommendations for improvement
        
        Format the response as a dictionary with these keys:
        - topics: List of main topics
        - patterns: List of identified study patterns
        - focus_areas: List of areas receiving most attention
        - gaps: List of potential knowledge gaps
        - recommendations: List of specific recommendations
        
        Transcripts:
        {combined}
        """
        
        # Generate the analysis
        response = model.generate_content(prompt)
        
        if not response.text:
            raise Exception("No analysis generated")
            
        # Parse and validate the response
        analysis = eval(response.text)  # Be careful with eval in production!
        
        # Validate the structure
        required_keys = ["topics", "patterns", "focus_areas", "gaps", "recommendations"]
        if not all(key in analysis for key in required_keys):
            raise Exception("Invalid analysis format")
            
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing study patterns: {str(e)}")
        raise Exception(f"Failed to analyze study patterns: {str(e)}")
