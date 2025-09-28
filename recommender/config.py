from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "unified_catalog" / "unified_courses.db"
INDEX_PATH = BASE_DIR / "course_index.faiss"

# --- Embedding model settings ---
# Choose either:
#   "sentence-transformers/all-mpnet-base-v2"  (768D, higher quality, ~1GB RAM)
#   "sentence-transformers/all-MiniLM-L6-v2"  (384D, very fast, ~250MB RAM)
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

# Retrieval parameters
TOP_K = 10   # number of nearest neighbors to return
