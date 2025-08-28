from pathlib import Path

# Base points to course-scraper/
BASE = Path(__file__).resolve().parents[1]

UNIFIED_DIR = BASE / "unified_catalog"
UNIFIED_DIR.mkdir(parents=True, exist_ok=True)
(UNIFIED_DIR / "logs").mkdir(parents=True, exist_ok=True)

# Source DBs
COURSERA_DB = BASE / "course-scraper" / "coursera_scraper" / "coursera.db"
EDX_DB = BASE / "course-scraper" / "edX_scraper" / "courses.db"
NPTEL_DB = BASE / "course-scraper" / "NPTEL_scraper" / "courses.db"

# Target unified DB
TARGET_DB = UNIFIED_DIR / "unified_courses.db"

# Logging
LOG_FILE = UNIFIED_DIR / "logs" / "etl_merge.log"

# ETL tuning
BATCH_SIZE = 500
DRY_RUN_DEFAULT = False

# Safety toggles
FAIL_FAST = False          # stop on first extractor error
SKIP_MISSING_SOURCES = True  # if a source DB is missing, skip it with a warning

# Reasonable defaults for normalization
DEFAULT_LANGUAGE = None
DEFAULT_LEVEL = None
DEFAULT_SUBJECT = None
DEFAULT_DURATION_WEEKS = None
