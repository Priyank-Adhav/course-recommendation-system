# Coursera Scraper

**Course-recommendation-system — `coursera_scraper` module**

A focused GraphQL-based scraper that harvests course metadata from Coursera and stores it in a local SQLite database. Designed for research and dataset-building (used as input to a course recommendation system). Supports searching by keyword or by Coursera domain slug (e.g., `business`, `computer-science`).

---

## Table of contents

- Features
- Project layout
- Requirements
- Setup
- Configuration
- Usage
- Database schema (summary)
- Logging & raw pages
- Best practices & notes
- Troubleshooting
- Development tips

---

## Features

- Query Coursera's public GraphQL gateway to retrieve course and specialization metadata.
- Two query modes:
  - **Keyword search** — query text (example: "python", "project management").
  - **Domain filter** — use Coursera domain slugs (example: "business", "computer-science") to get domain-specific results.
- Saves canonical course records to an SQLite database (`coursera.db`) with upsert semantics (no duplicate course rows).
- Records which query produced which course (mapping table) so you can filter results by the originating query.
- Saves raw GraphQL pages (JSON) for auditing and debugging.
- Simple CLI interface (`run_coursera.py`) with `initdb`, `test`, and `run` commands.
- Configurable page size and delay to control request volume.

---

## Project layout

```
coursera_scraper/
├── config.py                # config values (PAGE_SIZE, SEARCH_QUERIES, DB_PATH, etc.)
├── coursera.db              # SQLite DB (created by init_db)
├── coursera_scraper.log     # log file
├── requirements.txt
├── run_coursera.py          # CLI entrypoint (initdb, test, run)
├── initial_tests/           # small artifacts used during development (optional)
└── scraper/
    ├── coursera_scraper.py  # main scraper logic (fetch/persist)
    ├── graphql_client.py    # builds payloads & sends GraphQL requests
    ├── utils.py             # helper functions (session, json helpers)
```

---

## Requirements

- Python **3.10+** (development used Python 3.13)
- `pip` and a virtual environment are recommended
- Key Python packages (check `requirements.txt`):
  - `requests`
  - `json5`
  - `beautifulsoup4` (if used)
  - other helper libraries as required

---

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Priyank-Adhav/course-recommendation-system
   cd course-scraper/coursera_scraper/
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Linux/macOS
   .venv\Scripts\activate     # Windows (PowerShell)
   pip install -r requirements.txt
   ```

3. Initialize the database schema:
   ```bash
   python run_coursera.py initdb
   ```

---

## Configuration

Open `config.py` and edit:

- `DB_PATH` — path to SQLite DB (default `coursera.db`).
- `PAGE_SIZE` — GraphQL page size (how many results per request). Coursera may cap the maximum; test values.
- `REQUEST_DELAY` — delay (seconds) between requests for politeness.
- `SEARCH_QUERIES` — list of queries to run (keywords or domain slugs).

**Note:** When using domain filters, the scraper constructs facet filters like `["domainId:<slug>"]`. Ensure slugs match Coursera's UI slugs (`business`, `computer-science`, `data-science`, `information-technology`, ...).

---

## Usage

### Initialize DB (once)
```bash
python run_coursera.py initdb
```

### Test mode (single query, one page)
```bash
# keyword (no domain filter)
python run_coursera.py test "python" False

# domain filter (domain slug)
python run_coursera.py test "business" True
```

### Full run (iterate SEARCH_QUERIES)
```bash
# run all queries in config.py using keyword search
python run_coursera.py run False

# run all queries as domain filters
python run_coursera.py run True
```

---

## Database schema (summary)

Main tables created by `db/init_db.py`:

- `coursera_courses` — canonical course rows:
  - `id` (primary key)
  - `name`, `url`, `product_type`
  - `partners_json`, `skills_json`
  - `rating`, `num_ratings`, `difficulty`, `duration`, `tagline`
  - `fetched_at` (ISO timestamp)

- `coursera_course_search` — mapping table linking `query_text` → `course_id`:
  - `course_id`, `query_text`, `page_index`, `cursor`, `fetched_at`

- `coursera_raw_pages` — raw JSON pages saved:
  - `query_text`, `cursor`, `page_index`, `raw_json`, `fetched_at`

---

## Logging & raw pages

- Log file: `coursera_scraper.log` — contains INFO/WARNING/ERROR messages.
- Raw GraphQL responses saved in `coursera_raw_pages` for auditing and replay.

---

## Best practices & notes

- Respect rate limits — increase `REQUEST_DELAY` if you see 429 or many errors.
- Do not attempt to scrape behind login — this scraper uses public endpoints only.
- Check Coursera's terms and `robots.txt` if you plan to publish scraped data.
- Keep secrets and credentials out of the repository (.gitignore).

---

## Troubleshooting

- **400 Bad Request:** Ensure `facetFilters` are strings like `["domainId:business"]` (not dicts). Inspect logged payloads and server response preview.
- **DNS / network errors:** Retry, check network/DNS, or try a different network.
- **Duplicates:** The scraper upserts by course `id`; duplicates should not occur. If they do, verify `id` values.

---

## Development tips

- Use `python run_coursera.py test` for quick experiments.
- Use `sqlite3` or DB Browser for SQLite to inspect `coursera.db`.
- Keep `PAGE_SIZE` and `REQUEST_DELAY` configurable when tuning large runs.

---
