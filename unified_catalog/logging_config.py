import logging
import sys
from pathlib import Path
from .config import LOG_FILE

def setup_logger(name: str = "unified_catalog"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent double handlers if re-imported
    if logger.handlers:
        return logger

    # File handler
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.INFO)
    ffmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    fh.setFormatter(ffmt)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    cfmt = logging.Formatter("%(levelname)s: %(message)s")
    ch.setFormatter(cfmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.propagate = False
    return logger

logger = setup_logger()
