"""
Central configuration for the Wernicke-AI backend.

Every setting the app needs lives here, read from environment variables
(your .env file). Nothing else in the codebase should call os.getenv()
directly — it all comes through this module.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Storage locations -------------------------------------------------
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "data" / "uploads"))
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", BASE_DIR / "data" / "chroma_db"))
EVAL_LOG_PATH = Path(os.getenv("EVAL_LOG_PATH", BASE_DIR / "eval" / "eval_log.jsonl"))
RATE_LIMIT_STATE_PATH = Path(
    os.getenv("RATE_LIMIT_STATE_PATH", BASE_DIR / "data" / "rate_limit_state.json")
)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
EVAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# --- Embedding model -----------------------------------------------------
# Runs locally, no API key needed. Small (~80MB) and fast on CPU.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# --- Chunking --------------------------------------------------------------
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# --- Retrieval -------------------------------------------------------------
TOP_K = int(os.getenv("TOP_K", "4"))
# Below this similarity score, we refuse to answer instead of guessing.
MIN_RELEVANCE_SCORE = float(os.getenv("MIN_RELEVANCE_SCORE", "0.35"))

# --- Evaluation --------------------------------------------------------------
# Below this groundedness score, an answer gets flagged as a possible hallucination.
GROUNDEDNESS_THRESHOLD = float(os.getenv("GROUNDEDNESS_THRESHOLD", "0.35"))

# --- LLM provider: Gemini (free tier) ---------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

# --- Rate limiting & safety caps --------------------------------------------
DAILY_QUERY_LIMIT_GLOBAL = int(os.getenv("DAILY_QUERY_LIMIT_GLOBAL", "200"))
DAILY_QUERY_LIMIT_PER_IP = int(os.getenv("DAILY_QUERY_LIMIT_PER_IP", "20"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
MAX_DOCUMENTS = int(os.getenv("MAX_DOCUMENTS", "50"))

# --- Session isolation -------------------------------------------------------
# Header the frontend sends to identify a visitor's session.
SESSION_HEADER_NAME = os.getenv("SESSION_HEADER_NAME", "X-Session-ID")

# --- CORS ------------------------------------------------------------------
# Comma-separated list of origins allowed to call this API.
# "*" (default) allows everyone — fine for local dev, tighten before going live.
_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = ["*"] if _origins_raw.strip() == "*" else [o.strip() for o in _origins_raw.split(",")]

# --- App ---------------------------------------------------------------------
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
