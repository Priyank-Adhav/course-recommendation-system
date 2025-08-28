# run_coursera.py
import sys
from db.init_db import init_db
from scraper.coursera_scraper import run_all, test_one_query
from config import PAGE_SIZE, SEARCH_QUERIES

def help_msg():
    print("Usage:")
    print("  python run_coursera.py initdb")
    print("  python run_coursera.py run [use_domain_filter]")
    print("  python run_coursera.py test [query_text] [use_domain_filter]")
    print("    use_domain_filter: optional True/False (default False). If True, SEARCH_QUERIES must contain domain IDs (e.g., 'business', 'it').")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        help_msg()
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "initdb":
        init_db()
    elif cmd == "run":
        use_domain = False
        if len(sys.argv) >= 3:
            use_arg = sys.argv[2].lower()
            use_domain = use_arg in ("true","1","yes","y")
        run_all(queries=SEARCH_QUERIES, limit_per_query=PAGE_SIZE, use_domain_filter=use_domain)
    elif cmd == "test":
        # test mode: optional query_text and use_domain_filter
        query_text = None
        use_domain = False
        if len(sys.argv) >= 3:
            query_text = sys.argv[2]
        if len(sys.argv) >= 4:
            use_domain = sys.argv[3].lower() in ("true","1","yes","y")
        # run one page only (max_pages=1) by default
        test_one_query(query_text=query_text, use_domain_filter=use_domain, limit_per_page=PAGE_SIZE, max_pages=1)
    else:
        help_msg()
