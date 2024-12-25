import os
import aiofiles
import shutil
from pathlib import Path
from fastapi import UploadFile
from typing import Optional
import uuid

class FileStorage:
    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = Path(base_dir)
        self.audio_dir = self.base_dir / "audio"
        self.processed_dir = self.base_dir / "processed"
        self._create_directories()

    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile, user_id: int) -> str:
        """Save an uploaded file and return its path"""
        ext = Path(file.filename).suffix
        filename = f"{user_id}_{uuid.uuid4()}{ext}"
        file_path = self.audio_dir / filename

        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        return str(file_path)

    def save_processed(self, original_path: str, processed_data, sample_rate: int) -> str:
        """Save processed audio data and return its path"""
        import soundfile as sf
        
        original_name = Path(original_path).stem
        processed_name = f"{original_name}_processed.wav"
        processed_path = self.processed_dir / processed_name

        sf.write(str(processed_path), processed_data, sample_rate)
        return str(processed_path)

    async def get_file(self, file_path: str) -> Optional[Path]:
        """Get a file by its path"""
        path = Path(file_path)
        if not path.exists():
            return None
        return path

    async def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        path = Path(file_path)
        try:
            if path.exists():
                path.unlink()
                return True
        except Exception:
            pass
        return False

    def cleanup_old_files(self, max_age_days: int = 7):
        """Clean up files older than max_age_days"""
        import time
        current_time = time.time()
        
        for directory in [self.audio_dir, self.processed_dir]:
            for file_path in directory.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_days * 86400:  # Convert days to seconds
                        try:
                            file_path.unlink()
                        except Exception:
                            pass

# Create a global instance
storage = FileStorage(os.getenv("UPLOADS_DIR", "uploads"))
