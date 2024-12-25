import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import librosa
import soundfile as sf
import numpy as np
from pydub import AudioSegment
import google.generativeai as genai
from dotenv import load_dotenv
import tempfile
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)

# Create a thread pool executor for CPU-intensive tasks
executor = ThreadPoolExecutor(max_workers=3)

async def process_audio(input_path: str) -> str:
    """
    Process the audio file: reduce noise, normalize volume, and improve quality.
    Returns the path to the processed audio file.
    """
    try:
        # Create processed directory if it doesn't exist
        processed_dir = os.path.join(os.path.dirname(input_path), "processed")
        os.makedirs(processed_dir, exist_ok=True)

        # Generate output path
        filename = os.path.basename(input_path)
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(processed_dir, f"processed_{base_name}.m4a")

        def _process():
            try:
                # Load the audio file
                y, sr = librosa.load(input_path, sr=None)
                
                # Noise reduction using spectral gating
                S = librosa.stft(y)
                S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)
                noise_threshold = np.mean(S_db) - 1.5 * np.std(S_db)
                mask = S_db > noise_threshold
                S_clean = S * mask
                y_clean = librosa.istft(S_clean)

                # Normalize audio
                y_normalized = librosa.util.normalize(y_clean)

                # Save as temporary WAV file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                    sf.write(temp_wav.name, y_normalized, sr)
                    
                    # Convert to M4A
                    wav_audio = AudioSegment.from_wav(temp_wav.name)
                    wav_audio.export(output_path, format='ipod', 
                                  parameters=["-acodec", "aac", "-ac", "2", "-ab", "192k"])

                # Clean up temporary file
                os.unlink(temp_wav.name)

                return output_path
            except Exception as e:
                logger.error(f"Error in audio processing: {e}")
                raise

        # Run processing in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, _process)

        return result
    except Exception as e:
        logger.error(f"Error in process_audio: {e}")
        raise

async def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe the audio file using Gemini API.
    Returns the transcription text.
    """
    try:
        # Convert audio to text chunks
        def _get_audio_chunks():
            audio = AudioSegment.from_file(audio_path)
            chunk_length_ms = 30000  # 30 second chunks for better accuracy
            chunks = []
            
            for i in range(0, len(audio), chunk_length_ms):
                chunk = audio[i:i + chunk_length_ms]
                chunks.append(chunk)
            
            return chunks

        # Process chunk in thread pool
        async def _process_chunk(chunk: AudioSegment, index: int) -> str:
            try:
                # Create temporary directory for chunks if it doesn't exist
                temp_dir = os.path.join(os.path.dirname(audio_path), "temp_chunks")
                os.makedirs(temp_dir, exist_ok=True)

                # Save chunk with unique name
                temp_path = os.path.join(temp_dir, f"chunk_{index}.wav")
                chunk.export(temp_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])

                try:
                    # Use Gemini API for speech-to-text
                    model = genai.GenerativeModel('gemini-pro')
                    prompt = f"Please transcribe this audio segment accurately, maintaining punctuation and speaker changes: {temp_path}"
                    response = model.generate_content(prompt)
                    
                    return response.text.strip()
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            except Exception as e:
                logger.error(f"Error processing chunk {index}: {e}")
                return ""

        # Get audio chunks
        chunks = _get_audio_chunks()
        
        # Process all chunks with index
        tasks = [_process_chunk(chunk, i) for i, chunk in enumerate(chunks)]
        transcriptions = await asyncio.gather(*tasks)
        
        # Combine transcriptions
        full_transcript = " ".join(filter(None, transcriptions))
        
        if not full_transcript.strip():
            raise ValueError("No text was transcribed from the audio")

        return full_transcript
    except Exception as e:
        logger.error(f"Error in transcribe_audio: {e}")
        raise
