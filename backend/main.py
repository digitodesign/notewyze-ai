from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import noisereduce as nr
import librosa
import soundfile as sf
import numpy as np
from pydub import AudioSegment
import webrtcvad
import tempfile
import os
import google.generativeai as genai
from supabase import create_client
from dotenv import load_dotenv
import ffmpeg

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
supabase = create_client(
    os.getenv("VITE_SUPABASE_URL"),
    os.getenv("VITE_SUPABASE_ANON_KEY")
)

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

class AudioProcessor:
    def __init__(self):
        self.vad = webrtcvad.Vad(3)  # Aggressiveness mode 3 (highest)
        
    async def process_audio(self, audio_file: UploadFile) -> str:
        try:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save uploaded file
                input_path = os.path.join(temp_dir, "input.wav")
                output_path = os.path.join(temp_dir, "processed.wav")
                
                with open(input_path, "wb") as buffer:
                    content = await audio_file.read()
                    buffer.write(content)
                
                # Load audio
                data, sample_rate = librosa.load(input_path, sr=None)
                
                # Noise reduction
                reduced_noise = nr.reduce_noise(y=data, sr=sample_rate)
                
                # Normalize audio
                normalized = librosa.util.normalize(reduced_noise)
                
                # Voice activity detection and silence removal
                frame_duration = 30  # ms
                frame_size = int(sample_rate * frame_duration / 1000)
                frames = librosa.util.frame(normalized, frame_length=frame_size, hop_length=frame_size)
                
                vad_frames = []
                for frame in frames.T:
                    if self.vad.is_speech(frame.tobytes(), sample_rate):
                        vad_frames.append(frame)
                
                if vad_frames:
                    processed_audio = np.concatenate(vad_frames)
                else:
                    processed_audio = normalized
                
                # Save processed audio
                sf.write(output_path, processed_audio, sample_rate)
                
                # Upload to Supabase storage
                with open(output_path, "rb") as f:
                    file_name = f"processed/{os.path.basename(audio_file.filename)}"
                    result = supabase.storage.from_("audio").upload(
                        file_name,
                        f.read(),
                        {"content-type": "audio/wav"}
                    )
                    
                    if result.error:
                        raise HTTPException(status_code=500, detail="Failed to upload processed audio")
                    
                    # Get public URL
                    public_url = supabase.storage.from_("audio").get_public_url(file_name)
                    return public_url
                    
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

audio_processor = AudioProcessor()

@app.get("/")
async def root():
    return {"message": "NoteWyze AI Backend is running!"}

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    """Process uploaded audio file"""
    if not file.filename.endswith('.wav'):
        raise HTTPException(status_code=400, detail="Only WAV files are supported")
    
    processed_url = await audio_processor.process_audio(file)
    return {"processedAudioUrl": processed_url}

@app.post("/transcribe")
async def transcribe_audio(audio_url: str):
    """Transcribe processed audio using Gemini API"""
    try:
        # Download audio from URL
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            result = supabase.storage.from_("audio").download(audio_url)
            temp_file.write(result)
            temp_file.flush()
            
            # Convert audio to text using Gemini
            response = model.generate_content(f"Transcribe this audio file: {temp_file.name}")
            transcript = response.text
            
            # Clean up temp file
            os.unlink(temp_file.name)
            
            return {"transcript": transcript}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-quiz")
async def generate_quiz(transcript: str):
    """Generate quiz questions from transcript using Gemini API"""
    try:
        prompt = f"""Based on this lecture transcript, generate 5 multiple choice questions:
        {transcript}
        
        Format the response as a JSON array of objects with the following structure:
        {{
            question: string,
            options: string[],
            correctAnswer: number (index of correct option)
        }}"""
        
        response = model.generate_content(prompt)
        quiz = response.text
        
        return {"quiz": quiz}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-research")
async def generate_research(transcript: str):
    """Generate research recommendations from transcript using Gemini API"""
    try:
        prompt = f"""Based on this lecture transcript, suggest 5 research papers or articles for further reading:
        {transcript}
        
        Format the response as a JSON array of objects with the following structure:
        {{
            title: string,
            description: string,
            relevance: string (brief explanation of why it's relevant)
        }}"""
        
        response = model.generate_content(prompt)
        recommendations = response.text
        
        return {"recommendations": recommendations}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
