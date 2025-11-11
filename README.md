# Course Recommendation System

A modular and extensible pipeline for aggregating online course data (Coursera, edX, NPTEL), unifying and enriching it, generating embeddings, and serving personalized course recommendations. The system supports both query-based search and adaptive recommendations driven by user quiz performance.

## Repository Structure

```
course-recommendation-system/
├── course-scraper/              # Individual scrapers for Coursera, edX, NPTEL → SQLite
├── unified_catalog/             # ETL pipeline: merge three source DBs → unified SQLite
├── recommender/                 # Embeddings (FAISS), recommendation logic, FastAPI server
└── demo-quiz-app/               # Demo app (Flask backend + React/Vite frontend)
```

## End-to-End Data Flow

1. **Scraping and Collection**
   - Extract course metadata from:
     - Coursera → `course-scraper/coursera_scraper/coursera.db`
     - edX → `course-scraper/edX_scraper/courses.db`
     - NPTEL → `course-scraper/NPTEL_scraper/courses.db`

2. **Data Integration**
   - Normalize and merge into a unified schema using:
     ```bash
     python unified_catalog/etl.py --sources coursera edx nptel
     ```
   - Output: `unified_catalog/unified_courses.db`

3. **Feature Construction**
   - Generate processed course text for embedding:
     ```bash
     python unified_catalog/feature_builder.py
     ```
   - Produces a `course_features` table with `title`, `tags`, `level`, and `language`.

4. **Embedding & Indexing**
   - Encode text features using a Sentence-Transformer model (default: `all-mpnet-base-v2`) and build a FAISS index:
     ```bash
     python -c "from recommender.vector_store import build_optimized_index; build_optimized_index()"
     ```

5. **Recommendation API**
   - Serve recommendations using a FastAPI service:
     ```bash
     uvicorn recommender.server:app --host 0.0.0.0 --port 8000
     ```
   - Optimized for sub-second responses with cached models, FAISS index, and course data.

6. **Quiz-Based Personalization**
   - A Flask backend in `demo-quiz-app/backend` aggregates user quiz history from `quiz_system.db` and integrates with the recommender API.
   - Personalized recommendations are generated from quiz performance:
     - Courses to **strengthen weak areas**
     - Courses for **advanced exploration** based on strong performance
     - Courses **aligned with interests** inferred from attempted quizzes

7. **Frontend Integration**
   - `demo-quiz-app/frontend-vite/` displays results in three sections:
     - “You may want to improve in...”
     - “You performed well in... try these advanced courses”
     - “You’ve shown interest in... these may interest you”
   - The user can still perform manual course searches from the same interface.

## Unified Catalog Overview

- **Schema**
  - `unified_courses(course_id, source, title, description, url, provider, subject, level, language, tags_json, skills_json, ...)`
  - `course_features(course_id, title, tags, level, language)`
- **Processing**
  - Text is normalized using NLTK tokenization, stopword removal, and lemmatization.
  - URLs for Coursera are automatically prefixed with `https://www.coursera.org/` when needed.

## Recommender Details

- **Model**: `sentence-transformers/all-mpnet-base-v2` (768D)
  - Can be switched to a lighter alternative like `all-MiniLM-L6-v2`.
- **Index**: FAISS inner-product search on normalized vectors (cosine similarity).
- **API Endpoints**
  - `/recommend?query=<text>&top_k=10`
  - Integrated quiz-driven route: `/api/user_recommendations?user_id=<id>`

## Demo Quiz Application

### Backend (Flask)
- Acts as a proxy to the recommendation engine.
- New endpoints:
  - `/api/recommendations`: direct search-based recommendations
  - `/api/user_recommendations`: personalized recommendations based on quiz scores and recency

### Frontend (React + Vite)
- Displays search-based and personalized recommendations.
- Fetches user data (including `user.id` from local storage) and quiz-based results dynamically.

## How to Start

- Run Quiz Application:
  ```bash
  cd demo-quiz-app
  ./dev.sh
  ```
- Run Recommender API:
  ```bash
  cd recommender
  uvicorn server:app --reload --host 0.0.0.0 --port 8000
  ```

## Quickstart

1. Run scrapers to collect data.
2. Merge sources into a unified catalog.
3. Build course features.
4. Build the FAISS index.
5. Start the FastAPI recommender.
6. Run the Flask backend and React frontend for the demo app.

## Requirements

- **Python 3.10+**
- **Core libraries** (installed per component):
  - `sentence-transformers`, `faiss-cpu`, `numpy`, `fastapi`, `uvicorn`, `flask`, `requests`
  - `nltk`, `sqlite3`, `pandas`, `beautifulsoup4` (for scrapers)
- **Node.js** 18+ for the Vite frontend.

## Notes

- All embeddings and FAISS indexes must be rebuilt if the model or course features change.
- Optimized vector loading and caching minimize memory overhead during repeated queries.
- The personalized recommendation service considers quiz accuracy, quiz recency, and topic relevance to rank courses.
