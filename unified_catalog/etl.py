import argparse
import os
import sqlite3
from typing import Iterator, Dict, List

from .config import (
    COURSERA_DB,
    EDX_DB,
    NPTEL_DB,
    TARGET_DB,
    BATCH_SIZE,
    DRY_RUN_DEFAULT,
    FAIL_FAST,
    SKIP_MISSING_SOURCES,
)
from .logging_config import logger
from .db import open_conn
from .loader import ensure_schema, bulk_upsert
from .extractors import extract_coursera, extract_edx, extract_nptel

def _exists(path) -> bool:
    try:
        return os.path.exists(path)
    except Exception:
        return False

def run(sources: List[str], dry_run: bool = DRY_RUN_DEFAULT, batch_size: int = BATCH_SIZE):
    logger.info("ETL start — sources=%s dry_run=%s target=%s", sources, dry_run, TARGET_DB)

    # Connect target & ensure schema
    tgt = open_conn(TARGET_DB)
    ensure_schema(tgt)

    # For each source, open conn if present & extract
    # Stream into loader in batches to keep memory bounded
    for src in sources:
        src_l = src.lower().strip()
        if src_l == "coursera":
            path = COURSERA_DB
            extractor = extract_coursera
        elif src_l == "edx":
            path = EDX_DB
            extractor = extract_edx
        elif src_l == "nptel":
            path = NPTEL_DB
            extractor = extract_nptel
        else:
            logger.error("Unknown source: %s (skipping)", src)
            continue

        if not _exists(path):
            msg = f"Source DB missing for {src}: {path}"
            if SKIP_MISSING_SOURCES:
                logger.warning(msg + " — skipping.")
                continue
            else:
                raise FileNotFoundError(msg)

        logger.info("Processing source=%s DB=%s", src, path)
        src_conn = sqlite3.connect(str(path))
        src_conn.row_factory = sqlite3.Row

        try:
            generator = extractor(src_conn)

            if dry_run:
                # Count and log some samples without writing
                preview = []
                count = 0
                for rec in generator:
                    if count < 3:
                        preview.append(rec)
                    count += 1
                logger.info("[DRY RUN] %s produced %d normalized records. Preview:\n  1) %s\n  2) %s\n  3) %s",
                            src, count,
                            preview[0] if len(preview) > 0 else None,
                            preview[1] if len(preview) > 1 else None,
                            preview[2] if len(preview) > 2 else None)
            else:
                # Stream into upsert in batches
                buffer: List[Dict] = []
                c = 0
                for rec in generator:
                    buffer.append(rec)
                    if len(buffer) >= batch_size:
                        bulk_upsert(tgt, buffer, batch_size=batch_size)
                        c += len(buffer)
                        buffer.clear()
                if buffer:
                    bulk_upsert(tgt, buffer, batch_size=batch_size)
                    c += len(buffer)
                logger.info("Source %s: inserted/updated %d records", src, c)

        except Exception as e:
            logger.exception("Extractor failed for source=%s: %s", src, e)
            if FAIL_FAST:
                raise
        finally:
            src_conn.close()

    tgt.close()
    logger.info("ETL finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge Coursera/edX/NPTEL into a unified SQLite catalog")
    parser.add_argument("--sources", nargs="*", default=["coursera", "edx", "nptel"],
                        help="Which sources to include (default: all)")
    parser.add_argument("--dry-run", action="store_true", default=DRY_RUN_DEFAULT,
                        help="Run extractors and log preview without writing to the target DB")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Upsert batch size")
    args = parser.parse_args()

    run(args.sources, dry_run=args.dry_run, batch_size=args.batch_size)
