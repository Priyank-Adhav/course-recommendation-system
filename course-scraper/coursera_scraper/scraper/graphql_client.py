# scraper/graphql_client.py
import json
import time
import logging
from scraper.utils import make_session
from config import GRAPHQL_URL, HEADERS

logger = logging.getLogger("coursera_scraper.graphql_client")

# Minimal GraphQL query string focusing on fields we need
SEARCH_QUERY = """
query Search($requests: [Search_Request!]!) {
  SearchResult {
    search(requests: $requests) {
      elements {
        ...SearchProductHit
        __typename
      }
      pagination {
        cursor
        totalElements
        __typename
      }
    }
  }
}

fragment SearchProductHit on Search_ProductHit {
  id
  name
  url
  partners
  productType
  skills
  avgProductRating
  numProductRatings
  productDifficultyLevel
  productDuration
  tagline
}
"""

def build_payload(limit=50, cursor="0", query_text="", facet_filters=None):
    facet_filters = facet_filters or []
    payload = [
        {
            "operationName": "Search",
            "variables": {
                "requests": [
                    {
                        "entityType": "PRODUCTS",
                        "limit": limit,
                        "disableRecommender": True,
                        "maxValuesPerFacet": 1000,
                        "facetFilters": facet_filters,
                        "cursor": cursor,
                        "query": query_text
                    }
                ]
            },
            "query": SEARCH_QUERY
        }
    ]
    return payload

def _post_with_retries(session, url, json_payload, headers, timeout=30, max_attempts=5):
    """
    POST with exponential backoff for transient network errors.
    Returns requests.Response on success, raises on non-transient failures.
    """
    backoff = 1.0
    for attempt in range(1, max_attempts + 1):
        try:
            r = session.post(url, json=json_payload, headers=headers, timeout=timeout)
            return r
        except Exception as e:
            # catch DNS errors, connection resets, timeouts etc.
            logger.warning("Network error on attempt %d/%d: %s — backing off %.1fs", attempt, max_attempts, e, backoff)
            if attempt == max_attempts:
                logger.exception("Max retries reached for post; raising.")
                raise
            time.sleep(backoff)
            backoff *= 2.0

def send_search(payload, headers=None, session=None, timeout=30):
    """
    Sends the GraphQL payload and returns parsed JSON.
    Throws requests.exceptions.HTTPError for non-2xx responses after saving response text to logs.
    """
    session = session or make_session()
    headers = headers or HEADERS

    r = _post_with_retries(session, GRAPHQL_URL, payload, headers, timeout=timeout)

    # Helpful debugging: log response text when not OK
    if r.status_code != 200:
        text_preview = (r.text[:2000] + '...') if len(r.text) > 2000 else r.text
        logger.error("GraphQL returned status %s. Response body (preview):\n%s", r.status_code, text_preview)
        # raise for upstream handling
        r.raise_for_status()

    # Normal case
    try:
        return r.json()
    except Exception as e:
        logger.exception("Failed to parse JSON from GraphQL response: %s", e)
        raise

def extract_results(resp_json):
    """
    Normalize different shapes and extract:
      - elements: list of product objects
      - cursor: string (for pagination)
      - totalElements: integer or None
    """
    data_root = None
    if isinstance(resp_json, list) and len(resp_json) > 0 and isinstance(resp_json[0], dict) and 'data' in resp_json[0]:
        data_root = resp_json[0]['data']
    elif isinstance(resp_json, dict) and 'data' in resp_json:
        data_root = resp_json['data']
    else:
        logger.debug("Unexpected GraphQL response shape: %s", type(resp_json))
        return [], None, None

    try:
        search_arr = data_root.get('SearchResult', {}).get('search') or []
        if isinstance(search_arr, list) and len(search_arr) > 0:
            search_obj = search_arr[0]
        else:
            search_obj = search_arr if isinstance(search_arr, dict) else {}
        elements = search_obj.get('elements') or []
        pagination = search_obj.get('pagination') or {}
        cursor = pagination.get('cursor')
        total = pagination.get('totalElements')
        return elements, cursor, total
    except Exception as e:
        logger.exception("Error extracting results: %s", e)
        return [], None, None

# Helper: try multiple facet key names if the server rejects the first
def try_facet_variants(limit, cursor, query_text, domain_id, session=None, headers=None, timeout=30):
    """
    Attempt the search using several plausible facet key names. Returns (resp_json, used_variant)
    or raises the last exception.
    """
    session = session or make_session()
    headers = headers or HEADERS

    # FIXED: Use string format instead of object format
    facet_variants = [
        [f"domainId:{domain_id}"],
        [f"domain:{domain_id}"],
        [f"domain_slug:{domain_id}"],
        [f"category:{domain_id}"],
        [f"subjectArea:{domain_id}"],
        [f"subject:{domain_id}"],
        [f"productDifficultyLevel:{domain_id}"],  # This might not work for domain filtering but worth trying
    ]

    last_exc = None
    for fv in facet_variants:
        payload = build_payload(limit=limit, cursor=cursor, query_text="", facet_filters=fv)
        try:
            resp_json = send_search(payload, headers=headers, session=session, timeout=timeout)
            # if send_search did not raise, consider it success
            logger.info("Facet variant worked: %s", fv)
            return resp_json, fv
        except Exception as e:
            last_exc = e
            logger.warning("Facet variant %s failed: %s", fv, e)
            # continue trying
    # all variants failed
    logger.error("All facet variants failed for domain_id=%s", domain_id)
    raise last_exc