# config.py

# SQLite DB path
DB_PATH = "coursera.db"

# Per-request page size (Coursera may cap this; 50–100 is typical)
PAGE_SIZE = 500

# Pause between requests (seconds)
REQUEST_DELAY = 1.5

# Headers to send with requests (do not include sensitive cookies)
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; CourseCatalogScraper/1.0)"
}

# Edit this list to control what searches you run.
# Each entry can be a keyword query (e.g., "computer science") or a domainId filter like "business" or "data-science".
# The scraping code will try both styles: if you want domain filtering, set 'use_domain_filter' True in run options.
SEARCH_QUERIES = [
    "computer-science",
    "business",
    "data-science",
    "it",
    "arts-and-humanities",
    "health",
    "math-and-logic",
    "personal-development",
    "physical-science-and-engineering",
    "social-sciences",
    "language-learning",
]

# GraphQL endpoint
GRAPHQL_URL = "https://www.coursera.org/graphql-gateway?opname=Search"
