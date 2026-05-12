import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMMA_API_KEY")
if not API_KEY:
    # Use a clear error message if the key is missing
    raise RuntimeError("GEMMA_API_KEY not found in environment or .env file.")

MAX_DIFF_LENGTH = 15000  # Max characters for the diff (fallback for token counting)

# Default patterns to ignore in git diffs to reduce noise
DEFAULT_IGNORES = [
    "*.lock", 
    "package-lock.json", 
    "yarn.lock", 
    "*.pyc", 
    "__pycache__/*", 
    "venv/*", 
    "node_modules/*",
    "*.min.js",
    "*.map"
]

MODEL_31B = "models/gemma-4-31b-it"
MODEL_26B = "models/gemma-4-26b-a4b-it"

DEFAULT_PERSONA = "senior"
