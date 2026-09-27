import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")

MAX_STEPS = 8

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage", "data")
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage", "uploads")
