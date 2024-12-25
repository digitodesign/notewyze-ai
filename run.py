import subprocess
import sys
import time
import webbrowser
import logging
import signal
import psutil
from pathlib import Path
from setup import setup_backend, setup_frontend, check_environment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global process list
processes = []

def kill_process_tree(process):
    """Kill a process and all its children."""
    try:
        parent = psutil.Process(process.pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass

def cleanup():
    """Clean up all running processes."""
    logger.info("Cleaning up processes...")
    for process in processes:
        kill_process_tree(process)

def run_backend():
    """Run the FastAPI backend server"""
    backend_dir = Path("backend")
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
            cwd=str(backend_dir)
        )
        processes.append(process)
        logger.info("✅ Backend server started at http://localhost:8000")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to start backend server: {e}")
        return False

def run_frontend():
    """Run the React frontend development server"""
    frontend_dir = Path("notewyze-ai")
    try:
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=str(frontend_dir)
        )
        processes.append(process)
        logger.info("✅ Frontend server started at http://localhost:3000")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to start frontend server: {e}")
        return False

def check_health():
    """Check if all services are healthy."""
    try:
        import httpx
        import asyncio
        
        async def check():
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/health")
                return response.json()
        
        health_status = asyncio.run(check())
        return health_status["status"] == "healthy"
    except Exception:
        return False

def signal_handler(signum, frame):
    """Handle termination signals."""
    logger.info("\n👋 Shutting down NoteWyze AI...")
    cleanup()
    sys.exit(0)

def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("🚀 Starting NoteWyze AI...")
    
    # Check environment
    if not check_environment():
        logger.error("Environment check failed")
        sys.exit(1)
    
    # Run setup if needed
    try:
        setup_needed = input("Do you want to run setup? (y/N): ").lower() == 'y'
        if setup_needed:
            if not setup_backend() or not setup_frontend():
                logger.error("Setup failed")
                sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
    
    # Start services
    if not run_backend():
        cleanup()
        sys.exit(1)
    
    time.sleep(2)  # Wait for backend to start
    
    if not run_frontend():
        cleanup()
        sys.exit(1)
    
    time.sleep(2)  # Wait for frontend to start
    
    # Check health
    if not check_health():
        logger.warning("⚠️ Some services might not be healthy. Check http://localhost:8000/health for details.")
    
    # Open browser
    webbrowser.open("http://localhost:3000")
    
    logger.info("\n🎉 NoteWyze AI is running!")
    logger.info("📝 Backend API docs: http://localhost:8000/docs")
    logger.info("🖥️ Frontend app: http://localhost:3000")
    logger.info("Press Ctrl+C to stop all services")
    
    # Keep the script running and monitor processes
    while True:
        if any(process.poll() is not None for process in processes):
            logger.error("❌ One or more services crashed!")
            cleanup()
            sys.exit(1)
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        cleanup()
        sys.exit(1)
