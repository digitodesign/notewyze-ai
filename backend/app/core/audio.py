import os
import io
import tempfile
from typing import Tuple, Union
import soundfile as sf
import librosa
import numpy as np
from pydub import AudioSegment

def process_audio_file(file_input: Union[str, bytes]) -> Tuple[str, float]:
    """
    Process an audio file to get its duration and format.
    Args:
        file_input: Either a file path (str) or bytes of the audio file
    Returns:
        Tuple of (file_path, duration)
    """
    try:
        # Create a temporary file if input is bytes
        if isinstance(file_input, bytes):
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(file_input)
                temp_file_path = temp_file.name
            audio = AudioSegment.from_wav(temp_file_path)
            file_path = temp_file_path
        else:
            audio = AudioSegment.from_file(file_input)
            file_path = file_input
            
        duration = len(audio) / 1000.0  # Convert to seconds
        return file_path, duration
    except Exception as e:
        raise Exception(f"Error processing audio file: {str(e)}")

def extract_transcript(file_path: str) -> str:
    """
    Extract transcript from audio file using speech recognition
    For now, this is a placeholder that returns a dummy transcript
    In production, you would integrate with a proper speech-to-text service
    """
    try:
        # Placeholder for actual speech-to-text implementation
        return "This is a placeholder transcript. Implement actual speech-to-text service integration."
    except Exception as e:
        raise Exception(f"Error extracting transcript: {str(e)}")

def convert_to_wav(file_path: str) -> str:
    """
    Convert audio file to WAV format if it isn't already
    """
    try:
        # Create a temporary directory to store the converted file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            audio = AudioSegment.from_file(file_path)
            audio.export(temp_file.name, format='wav')
            return temp_file.name
    except Exception as e:
        raise Exception(f"Error converting audio to WAV: {str(e)}")

def get_audio_features(file_path: str) -> dict:
    """
    Extract audio features using librosa
    """
    try:
        # Load the audio file
        y, sr = librosa.load(file_path)
        
        # Extract features
        features = {
            'tempo': librosa.beat.tempo(y=y, sr=sr)[0],
            'rms': float(np.mean(librosa.feature.rms(y=y))),
            'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(y=y))),
            'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
        }
        
        return features
    except Exception as e:
        raise Exception(f"Error extracting audio features: {str(e)}")
