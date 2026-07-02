import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
API_URL = os.getenv("API_URL", "https://api.escuelajs.co/api/v1/products")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set in the .env file.")
