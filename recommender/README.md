# Recommender — Semantic Course Search

This component builds and serves a semantic search index over the unified course catalog. It embeds course features using a Sentence-Transformer model, indexes them with FAISS, and exposes a FastAPI endpoint for top‑K recommendations.

## Contents

- Overview
- Data dependencies
- Embedding & indexing
- Inference flow
- API
- Configuration
- Running locally
- Performance notes
- Troubleshooting

## Overview

Files in this folder:

- `config.py` — Paths and knobs (database, index location, embedding model, default `TOP_K`).
- `vector_store.py` — Index builder and runtime singletons for model, FAISS index, course cache; warmup utility.
- `recommend.py` — Core `recommend(query, top_k)` function.
- `server.py` — FastAPI app that exposes `GET /recommend`.
- `requirements.txt` — Python dependencies.
- `course_index.faiss` / `course_index.faiss_ids.npy` — Generated FAISS index + course ID mapping (created after indexing).

## Data dependencies

The recommender expects a unified SQLite database created by the `unified_catalog` ETL:

- Input DB (from `config.DB_PATH`): `../unified_catalog/unified_courses.db`
- Required tables:
  - `unified_courses(course_id, title, url, provider, level, ...)` — used for response enrichment and caching.
  - `course_features(course_id, title, tags, ...)` — used at index build time. The `tags` field is a normalized combination of subject, skills, tags, title, and description.

If `course_features` does not exist, run `unified_catalog/feature_builder.py` first.

## Embedding & indexing

- Model: configured via `config.EMBEDDING_MODEL`.
  - Default: `sentence-transformers/all-mpnet-base-v2` (768‑dim, higher quality).
  - Alternative noted in code comments: `sentence-transformers/all-MiniLM-L6-v2` (384‑dim, faster/lower memory).
- Text for embedding (from `vector_store.build_optimized_index`):
  - `f"{title_clean}. {tags_clean}"` per row from `course_features`.
- Encoder: `SentenceTransformer.encode(..., convert_to_numpy=True, batch_size=32, show_progress_bar=True)`.
- Index: `faiss.IndexFlatIP(dim)` with L2 normalization of vectors, so inner product equals cosine similarity.
- Artifacts:
  - FAISS index written to `config.INDEX_PATH` (default: `recommender/course_index.faiss`).
  - Course ID array saved to `recommender/course_index.faiss_ids.npy`.

Build the index:

```bash
python -c "from recommender.vector_store import build_optimized_index; build_optimized_index()"
```

GPU note: if GPUs are available and there are more than 1000 items, the builder temporarily uses a GPU index for faster add, then moves back to CPU (`faiss.index_gpu_to_cpu`).

## Inference flow

- The API uses a singleton `OptimizedVectorStore` to lazily load and cache:
  - the Sentence-Transformer model,
  - the FAISS index and the `course_ids` array,
  - a course data cache (from `unified_courses` columns: `title`, `url`, `provider`, `level`).
- Query handling (`recommend.py`):
  1. Encode the input `query` as a single vector (batch size 1).
  2. L2 normalize the query vector.
  3. `index.search(query_vec, top_k)` to retrieve nearest neighbors.
  4. For each hit, map index → `course_id` using the saved ID array.
  5. Look up `title`, `url`, `provider`, `level` from the course cache.
  6. Return a list of `{ course_id, title, url, provider, level, score }`.

Warmup:

```bash
python -c "from recommender.vector_store import warmup_system; warmup_system()"
```

This loads model, index, cache, and runs a small test query to prime weights and memory pages.

## API

FastAPI app: `server.py`

- `GET /recommend`
  - Query parameters:
    - `query` (string, required): the search query.
    - `top_k` (integer, optional, default 10): number of results.
  - Response: JSON array of objects with keys: `course_id`, `title`, `url`, `provider`, `level`, `score`.

Example:

```bash
uvicorn recommender.server:app --host 0.0.0.0 --port 8000
curl --get 'http://localhost:8000/recommend' --data-urlencode 'query=python data analysis' --data 'top_k=5'
```

## Configuration

`config.py` controls the main parameters:

- Paths
  - `DB_PATH` — unified catalog SQLite path (default: `../unified_catalog/unified_courses.db`).
  - `INDEX_PATH` — FAISS index target (default: `./course_index.faiss`).
- Embedding model
  - `EMBEDDING_MODEL` — e.g., `sentence-transformers/all-mpnet-base-v2`.
- Retrieval
  - `TOP_K` — default number of results if the caller does not specify.

Switching models: if you change `EMBEDDING_MODEL`, you must rebuild the FAISS index for dimensionality and distribution compatibility.

## Running locally

1) Install dependencies:

```bash
python -m pip install -r recommender/requirements.txt
```

2) Ensure upstream data exists:

- `unified_catalog/unified_courses.db` present
- `course_features` table populated (run `python unified_catalog/feature_builder.py` if not)

3) Build the FAISS index:

```bash
python -c "from recommender.vector_store import build_optimized_index; build_optimized_index()"
```

4) Start the API:

```bash
uvicorn recommender.server:app --host 0.0.0.0 --port 8000
```

## Performance notes

- Model load time: one-time on first use (or during warmup). The singleton keeps it in memory.
- Index search is O(top_k + dim) per query with `IndexFlatIP`. For large catalogs, consider IVF/HNSW variants if latency grows.
- Memory:
  - `all-mpnet-base-v2` embeddings are 768‑dim float32 vectors ≈ 3 KB per course (before FAISS overhead). 100k courses ≈ ~300 MB for vectors alone.
  - `all-MiniLM-L6-v2` reduces dimension to 384 (
≈ 1.5 KB per course) at some quality tradeoff.
- Use GPU during build to accelerate add (automatic if available and dataset > 1000); runtime search is CPU in this setup.

## Troubleshooting

- Empty/low‑quality results:
  - Verify `course_features` exists and `tags` are non‑empty.
  - Rebuild index after changing features or model.
- Shape/compat errors:
  - Ensure index and model dimensions match (rebuild after switching models).
- Missing fields in response:
  - The response pulls from `unified_courses` cache; verify those columns exist and are populated.
- Import errors when running from root:
  - Use module paths or run commands from repository root so relative imports resolve.

---

This recommender is intentionally simple and transparent: content‑based retrieval via normalized cosine similarity over curated course features. It is a solid baseline that can be extended with re‑ranking, filters (e.g., language/level), hybrid BM25, or personalization signals.
