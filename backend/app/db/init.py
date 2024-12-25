import logging
import subprocess
from pathlib import Path
from app.db.session import check_db_connection
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database, run migrations, and create initial data."""
    try:
        # Check database connection
        if not check_db_connection():
            logger.error("Failed to connect to database")
            return False

        # Get the backend directory path
        backend_dir = Path(__file__).parent.parent.parent

        # Run database migrations
        try:
            logger.info("Running database migrations...")
            subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=str(backend_dir),
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Migration failed: {e.stderr}")
            return False

        # Create initial data if in development
        if settings.ENVIRONMENT == "development":
            from app.db.init_db import create_initial_data
            from app.db.session import get_db_context
            
            with get_db_context() as db:
                create_initial_data(db)

        logger.info("Database initialization completed successfully")
        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_database()
