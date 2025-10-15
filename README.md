# Course Recommendation System

A modular pipeline to scrape course catalogs (Coursera, edX, NPTEL), unify and enrich the data, generate vector embeddings, and serve a semantic search API that can be consumed by a demo quiz application.

## Repository Structure

```
course-recommendation-system/
├── course-scraper/              # Individual scrapers for Coursera, edX, NPTEL → SQLite
├── unified_catalog/           # ETL: merge three source DBs → unified SQLite
├── recommender/                   # Embeddings (FAISS), semantic search, FastAPI server
└── demo-quiz-app/                # Demo app (Flask backend + React/Vite frontend)
```

## End-to-End Data Flow

1. Scrape course data from providers and store in per-source SQLite DBs:
   - Coursera → `course-scraper/coursera_scraper/coursera.db`
   - edX → `course-scraper/edX_scraper/courses.db`
   - NPTEL → `course-scraper/NPTEL_scraper/courses.db`
2. Run ETL to normalize and merge into a single catalog:
   - Output: `unified_catalog/unified_courses.db` with canonical schema and a `source_map` table for traceability.
3. Build derived features for embedding:
   - `unified_catalog/feature_builder.py` creates `course_features(course_id, title, tags, level, language)` where `tags` combines subject, skills, tags, title, and description, normalized with NLTK.
4. Vectorize and index:
   - `recommender/vector_store.py` encodes text using a Sentence-Transformer model and builds a FAISS index alongside ID mapping files.
5. Serve recommendations:
   - `recommender/server.py` exposes a `/recommend` endpoint. The demo app calls this via a proxy endpoint in its Flask backend.

## Scrapers

### Coursera (`course-scraper/coursera_scraper/`)
- Queries Coursera's public GraphQL.
- CLI: `run_coursera.py`
  - `python run_coursera.py initdb`
  - `python run_coursera.py run [use_domain_filter]`
  - `python run_coursera.py test [query_text] [use_domain_filter]`
- Config: `config.py` (e.g., `PAGE_SIZE`, `SEARCH_QUERIES`, `DB_PATH`).
- Output DB: `course-scraper/coursera_scraper/coursera.db`.

### edX (`course-scraper/edX_scraper/`)
- Script: `get.py` (writes to `courses.db`).
- Schema includes `courses`, `skills`, `tags`, `staff`, `owners` tables (see `README.md`).
- Output DB: `course-scraper/edX_scraper/courses.db`.

### NPTEL (`course-scraper/NPTEL_scraper/`)
- Catalog scraper + detail scraper (HTML + embedded JS parsing), rate-limited.
- CLI: `run_scraper.py`
  - `python run_scraper.py initdb`
  - `python run_scraper.py catalog`
  - `python run_scraper.py courses`
- Output DB: `course-scraper/NPTEL_scraper/courses.db`.

## Unified Catalog (ETL)

- Entry: `unified_catalog/etl.py`
- Merges Coursera, edX, and NPTEL into `unified_catalog/unified_courses.db`.
- Loader schema (`unified_catalog/loader.py`):
  - `unified_courses(course_id PRIMARY KEY, source, source_course_id, title, description, url, provider, instructors_json, subject, level, language, duration_weeks, tags_json, skills_json, rating, ratings_count, popularity, image_url, created_at, updated_at, extra_json)`
  - `source_map(course_id, source, source_course_id, raw_record_json, recorded_at)`
- Usage:
  - Dry-run preview:
    ```bash
    python unified_catalog/etl.py --dry-run --sources coursera edx nptel
    ```
  - Full run:
    ```bash
    python unified_catalog/etl.py --sources coursera edx nptel
    ```
  - Options: `--batch-size`, `--sources`, `--dry-run`.

### Feature Builder
- File: `unified_catalog/feature_builder.py`
- Creates `course_features` table:
  - `course_id`, `title`, `tags`, `level`, `language`
- `tags` is built by combining and normalizing subject, skills, tags, title, and description via NLTK lemmatization and stopword removal.
- Run:
  ```bash
  python unified_catalog/feature_builder.py
  ```

## Recommender (Embeddings + API)

### Embedding Model
- Defined in `recommender/config.py` as `EMBEDDING_MODEL`.
- Default: `sentence-transformers/all-mpnet-base-v2`.
  - Alternatives noted in config: `sentence-transformers/all-MiniLM-L6-v2` (faster, 384D) vs mpnet (higher quality, 768D).

### Index Build
- File: `recommender/vector_store.py`
- Reads `unified_catalog/unified_courses.db` → `course_features(title, tags)` and builds text `"{title}. {tags}"`.
- Encodes with the chosen Sentence-Transformer model, normalizes, and writes:
  - FAISS index: `recommender/course_index.faiss`
  - ID mapping: `recommender/course_index.faiss_ids.npy`
- Build (from repo root):
  ```bash
  python -c "from recommender.vector_store import build_optimized_index; build_optimized_index()"
  ```

### Serving API
- File: `recommender/server.py` (FastAPI)
- Endpoint: `GET /recommend`
  - Query params:
    - `query` (string, required)
    - `top_k` (int, default 10)
  - Response: list of objects containing at least `course_id`, `title`, `url`, `provider`, `level`, `score`.
- Local run:
  ```bash
  pip install -r recommender/requirements.txt
  uvicorn recommender.server:app --host 0.0.0.0 --port 8000
  ```

## Demo Quiz App

A separate example app that integrates with the recommendation API.

- Backend: Flask (`demo-quiz-app/backend/`)
  - Registers a proxy route `GET /api/recommendations` that forwards to the recommender API.
  - Env var: `RECOMMENDER_API_URL` (default `http://localhost:8000/recommend`).
  - Run (example):
    ```bash
    cd demo-quiz-app/backend
    pip install -r requirements.txt
    flask --app app:create_app run --port 5000
    ```
- Frontend (Vite/React, TypeScript): `demo-quiz-app/frontend-vite/`
  - Page: `src/pages/Recommendations.tsx` calls `http://localhost:5000/api/recommendations?query=...`
  - Run (example):
    ```bash
    cd demo-quiz-app/frontend-vite
    npm install
    npm run dev
    ```

## Quickstart

1. Scrape data (run any/all scrapers as desired to produce source DBs).
2. Merge into unified catalog:
   ```bash
   python unified_catalog/etl.py --sources coursera edx nptel
   ```
3. Build feature table:
   ```bash
   python unified_catalog/feature_builder.py
   ```
4. Build FAISS index:
   ```bash
   python -c "from recommender.vector_store import build_optimized_index; build_optimized_index()"
   ```
5. Start the recommender API:
   ```bash
   uvicorn recommender.server:app --host 0.0.0.0 --port 8000
   ```
6. Start the demo app backend and frontend (optional) and open the Recommendations page.

## Configuration

- `recommender/config.py`:
  - `EMBEDDING_MODEL` (default `sentence-transformers/all-mpnet-base-v2`)
  - `DB_PATH` (defaults to `unified_catalog/unified_courses.db`)
  - `INDEX_PATH` (defaults to `recommender/course_index.faiss`)
  - `TOP_K` (default 10)
- `unified_catalog/config.py`:
  - Paths for source DBs and unified target DB, batch sizes, toggles like `DRY_RUN_DEFAULT`, `SKIP_MISSING_SOURCES`.
- Scraper configs per provider under their respective `config.py` files.

## Requirements

- Python 3.10+
- Core libs (see each component's `requirements.txt`):
  - Recommender: `faiss-cpu`, `sentence-transformers`, `numpy`, `fastapi`, `uvicorn`
  - Unified catalog: see `unified_catalog/requirements.txt` (includes NLTK)
  - Scrapers: see each scraper folder (`requests`, `beautifulsoup4`, etc.)

## Notes

- The FAISS index and ID mapping are stored in `recommender/` and must match the model used. If you switch `EMBEDDING_MODEL`, rebuild the index.
- `feature_builder.py` downloads NLTK resources at runtime if missing (stopwords, punkt, wordnet).
- The system normalizes query and corpus vectors with L2 normalization and uses inner-product search (cosine similarity after normalization).

