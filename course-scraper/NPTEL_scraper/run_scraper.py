# run_scraper.py
import sys
from db import init_db
from scraper.catalog_scraper import run as run_catalog
from scraper.course_scraper import run as run_courses
from scraper.course_scraper import run_single as run_single

def help_msg():
    print("Usage:")
    print("  python run_scraper.py initdb     # create SQLite DB")
    print("  python run_scraper.py catalog    # fetch courses list and store course IDs")
    print("  python run_scraper.py courses    # fetch course pages and store metadata")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        help_msg()
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "initdb":
        init_db.init_db()
    elif cmd == "catalog":
        run_catalog()
    elif cmd == "courses":
        run_courses()
    else:
        help_msg()
