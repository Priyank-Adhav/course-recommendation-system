# Unified Catalog — README

**Location:** `course-recommendation-system/course-scraper/unified_catalog/`

## What this component does
This module merges course data scraped from multiple sources (Coursera, edX, NPTEL) into a single canonical SQLite database (`unified_courses.db`). It extracts, normalizes and upserts records from each source so downstream systems (embeddings, FAISS, recommender) can work from a single consistent catalog.

---

## Repo layout (important files)

```
unified_catalog/
├── config.py           # paths and ETL knobs
├── logging_config.py   # logger setup (logs/etl_merge.log)
├── etl.py              # main CLI driver (dry / run)
├── extractors.py       # source-specific extractors (coursera/edx/nptel)
├── transform.py        # normalization helpers
├── loader.py           # unified DB schema + upsert/bulk loader
├── db.py               # convenience DB/attach helpers
├── utils.py            # small utilities
├── helpers.py          # misc maintenance helpers (e.g. remove non-English)
├── unified_courses.db  # (created after running ETL)
└── tests/              # lightweight unit tests (pytest)
```

---

## Prerequisites

- Python 3.8+
- Install dependencies:

```bash
python -m pip install -r unified_catalog/requirements.txt
```

`requirements.txt` contains test packages (e.g. pytest) and any optional helpers. The ETL itself mostly uses the standard library.

---

## Basic usage

### Dry-run (inspect counts only)

Run a quick dry-run that extracts counts or previews without writing final DB changes:

```bash
python unified_catalog/etl.py dry
# or, if you prefer module style (add __init__.py first):
python -m unified_catalog.etl dry
```

### Full run (extract → transform → load)

This will create or update `unified_courses.db`:

```bash
python unified_catalog/etl.py run
# or
python -m unified_catalog.etl run
```

**Common options (if implemented):**

- `--batch <N>` — set insert batch size (tune for performance)

### Run a single helper

Run the included maintenance helper to delete non-English records:

```bash
python unified_catalog/helpers.py
```

### Tests

Run unit tests with pytest:

```bash
pytest unified_catalog/tests
```

---

## Output DB

Default file: `unified_catalog/unified_courses.db`

Loader ensures schema and uses UPSERT semantics so the ETL is idempotent.

**Recommended output tables:**

- `unified_courses` — canonical course rows (id, title, description, source, skills/tags JSON, level, language, url, fetched_at, etc.)
- `source_map` — traceability mapping back to original source IDs / raw JSON / query tag

---

## Notes & tips

- If you want to run `python -m unified_catalog.etl` add an `__init__.py` into `unified_catalog/`.
- The ETL is designed to be safe to re-run and will overwrite fields by upsert rules rather than duplicating.
- `loader.bulk_upsert()` uses batches and transactions — tune `batch_size` in `config.py` for your hardware.
- Logs are written to `unified_catalog/logs/etl_merge.log`.

---

## Git / DB files

The repo `.gitignore` purposely excludes SQLite WAL/SHM (`*.db-wal`, `*.db-shm`). If you want to commit the single `unified_courses.db`, keep the `.db` file tracked but leave WAL/SHM ignored. Warning: large DBs may bloat your Git history — consider using a release artifact or Git LFS.

---

## Troubleshooting

- **Import errors:** run from project root or add the project to `PYTHONPATH` (or use module form after adding `__init__.py`).
- **Missing source DBs:** ETL will skip missing inputs. Ensure scrapers produced the source DB files (Coursera, edX, NPTEL) and `config.py` has correct paths.
- **Slow runs:** ETL reads local SQLite DBs. If slow, increase batch sizes or run on a machine with faster disk I/O.