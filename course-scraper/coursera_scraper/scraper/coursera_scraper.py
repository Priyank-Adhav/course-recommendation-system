# scraper/coursera_scraper.py
import sqlite3
import time
import json
from datetime import datetime

from config import DB_PATH, PAGE_SIZE, REQUEST_DELAY, SEARCH_QUERIES
from scraper.utils import make_session, safe_json_dumps, setup_logger
from scraper.graphql_client import build_payload, send_search, extract_results, try_facet_variants

logger = setup_logger()  # logger name: coursera_scraper

def upsert_course(conn, item):
    cur = conn.cursor()
    cid = item.get('id')
    name = item.get('name')
    url = item.get('url')
    product_type = item.get('productType')
    partners = safe_json_dumps(item.get('partners') or [])
    skills = safe_json_dumps(item.get('skills') or [])
    rating = item.get('avgProductRating')
    num_ratings = item.get('numProductRatings')
    difficulty = item.get('productDifficultyLevel')
    duration = item.get('productDuration')
    tagline = item.get('tagline')
    fetched_at = datetime.utcnow().isoformat()

    try:
        cur.execute("""
        INSERT INTO coursera_courses(id, name, url, product_type, partners_json, skills_json, rating, num_ratings, difficulty, duration, tagline, fetched_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
          name=excluded.name,
          url=excluded.url,
          product_type=excluded.product_type,
          partners_json=excluded.partners_json,
          skills_json=excluded.skills_json,
          rating=excluded.rating,
          num_ratings=excluded.num_ratings,
          difficulty=excluded.difficulty,
          duration=excluded.duration,
          tagline=excluded.tagline,
          fetched_at=excluded.fetched_at
        """, (cid, name, url, product_type, partners, skills, rating, num_ratings, difficulty, duration, tagline, fetched_at))
        conn.commit()
    except Exception as e:
        logger.exception("Failed to upsert course %s: %s", cid, e)

def insert_course_search_mapping(conn, course_id, query_text, page_index, cursor):
    """
    Records that `course_id` was produced by `query_text` on page_index/cursor.
    Uses INSERT OR IGNORE because UNIQUE constraint prevents duplicates.
    """
    cur = conn.cursor()
    try:
        cur.execute("""
        INSERT OR IGNORE INTO coursera_course_search(course_id, query_text, page_index, cursor, fetched_at)
        VALUES(?,?,?,?,?)
        """, (course_id, query_text, page_index, cursor, datetime.utcnow().isoformat()))
        conn.commit()
    except Exception as e:
        logger.exception("Failed to insert mapping for course %s query=%s page=%s cursor=%s: %s", course_id, query_text, page_index, cursor, e)


def save_raw_page(conn, query_text, cursor, page_index, raw_json):
    cur = conn.cursor()
    try:
        # INSERT OR IGNORE because we created a UNIQUE constraint on (query_text, cursor, page_index)
        cur.execute("""
        INSERT OR IGNORE INTO coursera_raw_pages(query_text, cursor, page_index, raw_json, fetched_at)
        VALUES(?,?,?,?,?)
        """, (query_text, cursor, page_index, safe_json_dumps(raw_json), datetime.utcnow().isoformat()))
        conn.commit()
    except Exception as e:
        logger.exception("Failed to save raw page for query=%s cursor=%s page=%s: %s", query_text, cursor, page_index, e)

def fetch_all_for_query(
    query_text="",
    use_domain_filter=False,
    domain_id=None,
    limit_per_page=PAGE_SIZE,
    max_pages=None
):
    session = make_session()
    conn = sqlite3.connect(DB_PATH)
    cursor = "0"
    page_index = 0
    total_fetched = 0

    facet_filters = []
    used_facet_filters = None

    if use_domain_filter and domain_id:
        # FIXED: Use string format instead of object format
        facet_filters = [f"domainId:{domain_id}"]

    try:
        while True:
            if use_domain_filter and domain_id:
                try:
                    # First page (or if fallback not yet chosen): try facet variants
                    if used_facet_filters is None:
                        resp, used_facet_filters = try_facet_variants(
                            limit=limit_per_page,
                            cursor=cursor,
                            query_text="",  # no text when filtering by domain
                            domain_id=domain_id,
                            session=session
                        )
                        logger.info(
                            "Using facet variant=%s for domain_id=%s",
                            used_facet_filters,
                            domain_id
                        )
                    else:
                        # Reuse the working facet variant
                        payload = build_payload(
                            limit=limit_per_page,
                            cursor=cursor,
                            query_text="",
                            facet_filters=used_facet_filters
                        )
                        resp = send_search(payload, session=session)
                except Exception as e:
                    logger.exception(
                        "GraphQL request failed for domain_id=%s cursor=%s: %s",
                        domain_id, cursor, e
                    )
                    break
            else:
                # normal query_text-based search
                payload = build_payload(
                    limit=limit_per_page,
                    cursor=cursor,
                    query_text=query_text,
                    facet_filters=[]
                )
                try:
                    resp = send_search(payload, session=session)
                except Exception as e:
                    logger.exception(
                        "GraphQL request failed for query=%s cursor=%s: %s",
                        query_text, cursor, e
                    )
                    break

            # save raw page (INSERT OR IGNORE to avoid duplicates)
            save_raw_page(conn, query_text, cursor, page_index, resp)

            elements, next_cursor, total = extract_results(resp)
            if not elements:
                logger.info("No elements returned for query=%s cursor=%s", query_text, cursor)
                break

            for el in elements:
                upsert_course(conn, el)
                try:
                    insert_course_search_mapping(
                        conn,
                        el.get('id'),
                        query_text if not use_domain_filter else f"domain:{domain_id}",
                        page_index,
                        cursor
                    )
                except Exception:
                    pass
                total_fetched += 1

            logger.info(
                "Fetched %d items on page %d for query=%s (next_cursor=%s)",
                len(elements), page_index, query_text, next_cursor
            )
            page_index += 1

            if max_pages and page_index >= max_pages:
                logger.info("Reached max_pages=%s, stopping", max_pages)
                break

            if not next_cursor or next_cursor == cursor:
                logger.info("No further cursor returned; finished pagination for query=%s", query_text)
                break

            cursor = next_cursor
            time.sleep(REQUEST_DELAY)

    finally:
        conn.close()
        session.close()

    return total_fetched

def run_all(queries=SEARCH_QUERIES, limit_per_query=PAGE_SIZE, use_domain_filter=False):
    total = 0
    for q in queries:
        logger.info("Starting fetch for query: %s (domain_filter=%s)", q, use_domain_filter)
        if use_domain_filter:
            count = fetch_all_for_query(query_text="", use_domain_filter=True, domain_id=q, limit_per_page=limit_per_query)
        else:
            count = fetch_all_for_query(query_text=q, use_domain_filter=False, domain_id=None, limit_per_page=limit_per_query)
        logger.info("Finished query '%s' fetched %d records", q, count)
        total += count
    logger.info("Total fetched across queries: %d", total)
    return total

# ---------------------------
# Test helper (runs a single query and prints summary)
# ---------------------------
def test_one_query(query_text=None, use_domain_filter=False, domain_id=None, limit_per_page=PAGE_SIZE, max_pages=1):
    """
    Runs a single query (one or a few pages) and prints a short DB summary so you can inspect.
    """
    query_text = query_text or (SEARCH_QUERIES[0] if SEARCH_QUERIES else "")
    logger.info("TEST MODE: Running one query: %s (domain_filter=%s)", query_text, use_domain_filter)

    # run fetching for just a page or two (max_pages controls pages)
    count = fetch_all_for_query(query_text=query_text, use_domain_filter=use_domain_filter, domain_id=domain_id, limit_per_page=limit_per_page, max_pages=max_pages)
    logger.info("TEST MODE fetched %d items for query=%s", count, query_text)

    # show DB counts & a small sample
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM coursera_courses")
    total_courses = cur.fetchone()[0]
    cur.execute("SELECT id, name, url, skills_json FROM coursera_courses ORDER BY fetched_at DESC LIMIT 10")
    sample = cur.fetchall()
    conn.close()

    logger.info("DB now has %d courses (total). Showing up to 10 most recent:", total_courses)
    for r in sample:
        cid, name, url, skills = r
        logger.info(" - %s | %s | %s", cid, name, url)
        logger.debug("   skills: %s", skills)

    return count