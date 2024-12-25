import pytest
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Override database URL for testing
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)
