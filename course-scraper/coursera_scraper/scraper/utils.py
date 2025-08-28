# scraper/utils.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

logger = logging.getLogger(__name__)

def make_session(retries=3, backoff=0.5, status_forcelist=(429, 500, 502, 503, 504)):
    s = requests.Session()
    retries_cfg = Retry(total=retries, backoff_factor=backoff, status_forcelist=status_forcelist, allowed_methods=frozenset(["GET","POST"]))
    s.mount("https://", HTTPAdapter(max_retries=retries_cfg))
    s.mount("http://", HTTPAdapter(max_retries=retries_cfg))
    return s

def safe_json_dumps(obj):
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception as e:
        logger.debug("JSON dump failed: %s", e)
        return json.dumps(str(obj))

def setup_logger(log_file="coursera_scraper.log", level=logging.INFO):
    """
    Configure root logger to write to rotating file and console.
    Returns configured logger.
    """
    logger = logging.getLogger("coursera_scraper")
    if logger.handlers:
        # already configured
        return logger

    logger.setLevel(level)

    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Rotating file handler
    fh = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    fh.setLevel(level)
    fh_formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)

    # Console handler (INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)

    return logger
