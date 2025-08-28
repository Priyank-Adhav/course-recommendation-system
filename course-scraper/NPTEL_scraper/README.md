# NPTEL Scraper

**Course-recommendation-system — `NPTEL_scraper` module**

A focused scraper for NPTEL that harvests course metadata and lesson-level “Concepts Covered” tags, saving results in a local SQLite database. This module is part of a larger course-recommendation-system and is intended for research / dataset-building use.

---

## Table of contents

- [Overview](#overview)  
- [Features](#features)  
- [Project layout](#project-layout)  
- [Requirements](#requirements)  
- [Setup](#setup)  
- [How it works (high level)](#how-it-works-high-level)  
- [Configuration](#configuration)  
- [Usage](#usage)  
- [Database schema (summary)](#database-schema-summary)  
- [Parsing approach & heuristics](#parsing-approach--heuristics)  
- [Logging & robustness](#logging--robustness)  
- [Best practices & legal/ethical notes](#best-practices--legalethical-notes)  
- [Troubleshooting](#troubleshooting)  
- [Development tips](#development-tips)

---

## Overview

This scraper collects the NPTEL course catalog (course IDs, titles, institute, professors, URLs) and then visits each course page to extract lesson lists and the **“Concepts Covered”** strings that appear per lesson. Those strings are converted into structured tags (JSON arrays) and stored in a `course_metadata` table for later use as content-features in a recommendation model.

---

## Features

- Scrapes the NPTEL courses listing page to collect course IDs and basic metadata.
- Visits each course detail page and extracts per-lesson titles and the “Concepts Covered” text (used as tags).
- Stores canonical course records and lesson-level metadata into a local SQLite DB (`courses.db`).
- Uses resilient HTTP sessions with retries and polite rate-limiting.
- Parses embedded JavaScript objects when available (using `json5`) and falls back to HTML parsing.
- Split/normalize concept strings into JSON arrays for downstream ML use.

---

## Project layout

```
NPTEL_scraper/
├── config.py
├── courses.db              # SQLite DB (created via init_db)
├── data/                   # optional: saved artifacts / raw files
├── db/
│   └── init_db.py          # create DB schema
├── run_scraper.py          # CLI entrypoint: initdb, catalog, courses
├── requirements.txt
└── scraper/
    ├── catalog_scraper.py  # fetches courses list from /courses page
    ├── course_scraper.py   # fetches individual course pages + metadata
    └── utils.py            # helper functions (extract JS, split concepts, session)
```

---

## Requirements

- Python **3.10+** (development used Python 3.13)
- `pip` and a virtual environment recommended
- Dependencies found in `requirements.txt` (examples):
  - `requests`
  - `beautifulsoup4`
  - `json5`
  - `lxml`

---

## Setup

1. Clone repo and change directory:
   ```bash
   git clone https://github.com/Priyank-Adhav/course-recommendation-system
   cd course-scraper/NPTEL_scraper 
   ```

2. Create and activate a virtual environment, then install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Linux/macOS
   .venv\Scripts\activate       # Windows PowerShell
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python run_scraper.py initdb
   ```
   This creates `courses.db` and the tables `courses` and `course_metadata`.

---

## How it works (high level)

1. **Catalog step (`catalog_scraper.py`)**  
   - Downloads `https://nptel.ac.in/courses` and extracts an embedded JavaScript `courses` array (the page includes data assigned to a JS object).  
   - The helper `extract_js_courses_array()` in `scraper/utils.py` finds and parses that JS block using `json5` if necessary.  
   - Each course object (id, title, professor, institute, disciplineId, contentType, etc.) is upserted into the `courses` table.

2. **Course detail step (`course_scraper.py`)**  
   - Reads rows from `courses` where `scraped=0` and visits each `https://nptel.ac.in/courses/{course_id}`.  
   - Attempts to extract lesson-level data from an embedded `courseOutline` JS object (preferred). Lessons commonly include `concepts_covered`.  
   - If embedded JS is absent or parsing fails, falls back to HTML parsing (`BeautifulSoup`) to extract lessons and a global “Concepts Covered” block.  
   - Normalizes the concepts text into a JSON array of tags (using `split_concepts()`), then inserts into `course_metadata` one row per lesson.  
   - Marks the course `scraped=1` when lessons are saved.

---

## Configuration

Edit top-of-file constants in `scraper/course_scraper.py` to tune:

- `DB_PATH` — path to the sqlite DB (`courses.db`).
- `RATE_LIMIT_SECONDS` — delay between requests (default `0.5s`).
- `CONCURRENCY_LIMIT` — if you add parallel fetching, respect polite concurrency.
- `HEADERS` — HTTP headers (User-Agent). Do not set cookies or auth tokens for public scraping.

---

## Usage

### Initialize DB
```bash
python run_scraper.py initdb
```

### Get catalog (course list)
```bash
python run_scraper.py catalog
```
This populates the `courses` table with `course_id`, `title`, `institute`, `professor`, and URL.

### Fetch course pages and metadata
```bash
python run_scraper.py courses
```
This visits each unscraped course and writes lesson metadata to `course_metadata`.

---

## Database schema (summary)

File: `db/init_db.py` creates:

### `courses`
- `course_id` TEXT PRIMARY KEY
- `title` TEXT
- `institute` TEXT
- `professor` TEXT
- `content_type` TEXT
- `discipline_id` TEXT
- `current_run` INTEGER
- `self_paced` INTEGER
- `url` TEXT
- `scraped` INTEGER DEFAULT 0
- `last_updated` TEXT

### `course_metadata`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `course_id` TEXT (FK → courses.course_id)
- `lesson_number` INTEGER
- `lesson_title` TEXT
- `concepts_json` TEXT  -- JSON array string (e.g. ["thermodynamics","cycles"])
- `raw_concepts_text` TEXT
- `fetched_at` TEXT

---

## Parsing approach & heuristics

- **Preferred**: parse embedded JavaScript objects (many NPTEL pages embed `courseOutline` with `units`/`lessons` and `concepts_covered`). This yields clean lesson-level `concepts_covered` fields.
- **Fallback**: HTML parsing using selectors:
  - lesson titles: `ul.lessons-list li.lesson`
  - global concepts block: `<p class="mt-4"><b>Concepts Covered:</b> ...</p>`
- **Normalization**:
  - `split_concepts()` trims strings, splits on separators (`;`, `,`, `:`), lowercases or preserves case as desired.
  - If `concepts_covered` is a list (in JS), join with `; ` to normalize to a string before splitting.

---

## Logging & robustness

- `course_scraper.py` uses a `requests.Session()` with retries and backoff (`urllib3.Retry`) configured to handle transient errors and common HTTP 5xx responses.
- The scraper logs to stdout using Python `logging` — consider redirecting to a file or integrating a file handler for longer runs.
- Use `RATE_LIMIT_SECONDS` and `CONCURRENCY_LIMIT` to be polite and avoid throttling.

---

## Best practices & legal/ethical notes

- Check NPTEL's `robots.txt` (currently allows crawling) and Terms of Service before large-scale scraping or redistribution.
- Use respectful rate limits and avoid heavy concurrent requests that could harm the origin server.
- Attribute sources when you publish datasets derived from scraped content.

---

## Troubleshooting

- **No lessons found / empty concepts**:
  - Inspect the course page HTML: sometimes `courseOutline` structure differs slightly. Use saved raw HTML (or enable debug logging) to inspect embedded objects.
- **JSON5 parse errors**:
  - Pages sometimes include trailing commas or comments — `json5` is robust, but log the raw JS for debugging.
- **Network errors / DNS**:
  - Retries are enabled; persistent failures indicate networking issues or blocks; try a different network or throttle further.
- **Duplicate rows**:
  - `courses.course_id` is primary key; `upsert` logic in `catalog_scraper` prevents duplicate course rows. `course_metadata` entries are per lesson; if rerunning, consider dedup logic or mark `scraped` flags appropriately.

---

## Development tips

- Use `sqlite3 courses.db` or DB Browser for SQLite to inspect tables.
- For debugging a single course, use the `run_single(course_id, url)` helper in `scraper/course_scraper.py`.
- If you add parallel fetching, ensure you protect SQLite writes (use a queue/worker or thread-safe DB connections).

---

