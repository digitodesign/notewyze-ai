import importlib.util
import sys

def check_module(module_name):
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"[X] {module_name} is NOT installed")
        return False
    else:
        print(f"[+] {module_name} is installed")
        return True

# Core dependencies
modules = [
    'fastapi',
    'uvicorn',
    'sqlalchemy',
    'pydantic',
    'python-jose',
    'passlib',
    'python-multipart',
    'aiofiles',
    'alembic',
    'psycopg2',
    'asyncpg',
    'pydantic_settings',
    'python-dotenv',
    'google.generativeai',
    'numpy',
    'sklearn',
    'pydub',
    'ffmpeg',
    'soundfile',
    'librosa'
]

print("\nChecking dependencies...")
all_installed = all(check_module(module) for module in modules)

if all_installed:
    print("\n[+] All dependencies are installed!")
else:
    print("\n[X] Some dependencies are missing. Please run: pip install -r requirements.txt")
