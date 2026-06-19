import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "sk-or-v1-mock-key-antigravity")
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:5173")
SPECS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "specs")
