import os
import subprocess
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from backend/.env
backend_env_path = Path("backend/.env")
load_dotenv(backend_env_path)

def run_command(command, cwd=None):
    """Run a command and log its output."""
    try:
        process = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        return False

def setup_backend():
    """Set up the backend environment."""
    logger.info("Setting up backend...")
    backend_dir = Path("backend")
    
    # Install backend dependencies
    logger.info("Installing backend dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=str(backend_dir)):
        return False
    
    # Run database migrations
    logger.info("Running database migrations...")
    if not run_command([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=str(backend_dir)):
        return False
    
    return True

def setup_frontend():
    """Set up the frontend environment."""
    logger.info("Setting up frontend...")
    frontend_dir = Path("notewyze-ai")
    
    # Install frontend dependencies
    logger.info("Installing frontend dependencies...")
    if not run_command(["npm", "install"], cwd=str(frontend_dir)):
        return False
    
    # Build frontend (optional for development)
    logger.info("Building frontend...")
    if not run_command(["npm", "run", "build"], cwd=str(frontend_dir)):
        return False
    
    return True

def create_directories():
    """Create necessary directories."""
    logger.info("Creating necessary directories...")
    directories = [
        "backend/uploads",
        "backend/logs",
        "backend/app/static"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        "DATABASE_URL",
        "GEMINI_API_KEY",
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    return True

def main():
    """Main setup function."""
    logger.info("Starting NoteWyze AI setup...")
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    # Create necessary directories
    create_directories()
    
    # Setup backend
    if not setup_backend():
        logger.error("Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        logger.error("Frontend setup failed")
        sys.exit(1)
    
    logger.info("Setup completed successfully!")
    logger.info("You can now run the application using: python run.py")

if __name__ == "__main__":
    main()
