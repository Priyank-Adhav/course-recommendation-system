# debug_domains.py
import json
from scraper.utils import make_session
from scraper.graphql_client import build_payload, send_search

def debug_domain_search(domain_id):
    """Debug function to see what happens when we search with a domain filter"""
    session = make_session()
    
    # Try the domainId filter
    facet_filters = [f"domainId:{domain_id}"]
    payload = build_payload(
        limit=10,
        cursor="0",
        query_text="",
        facet_filters=facet_filters
    )
    
    try:
        resp = send_search(payload, session=session)
        print(f"\n=== Results for domainId:{domain_id} ===")
        print(f"Full response keys: {resp[0]['data'].keys() if isinstance(resp, list) else resp['data'].keys()}")
        
        # Extract just the search part
        if isinstance(resp, list):
            search_data = resp[0]['data']['SearchResult']['search'][0]
        else:
            search_data = resp['data']['SearchResult']['search'][0]
            
        elements = search_data.get('elements', [])
        pagination = search_data.get('pagination', {})
        
        print(f"Number of elements: {len(elements)}")
        print(f"Total elements: {pagination.get('totalElements', 'N/A')}")
        print(f"Cursor: {pagination.get('cursor', 'N/A')}")
        
        if elements:
            print(f"First element keys: {elements[0].keys()}")
            print(f"First element: {elements[0]['name']} ({elements[0]['id']})")
        else:
            print("No elements returned")
            
        # Let's also see if there are any facets or other metadata
        if 'facets' in search_data:
            print(f"Available facets: {search_data['facets']}")
            
    except Exception as e:
        print(f"Error for {domain_id}: {e}")
    finally:
        session.close()

def debug_general_search():
    """Debug function to see what a general search returns and what facets are available"""
    session = make_session()
    
    payload = build_payload(
        limit=10,
        cursor="0",
        query_text="computer science",  # General search
        facet_filters=[]
    )
    
    try:
        resp = send_search(payload, session=session)
        print(f"\n=== General search results ===")
        
        if isinstance(resp, list):
            search_data = resp[0]['data']['SearchResult']['search'][0]
        else:
            search_data = resp['data']['SearchResult']['search'][0]
            
        elements = search_data.get('elements', [])
        pagination = search_data.get('pagination', {})
        
        print(f"Number of elements: {len(elements)}")
        print(f"Total elements: {pagination.get('totalElements', 'N/A')}")
        
        # Look at a few elements to understand the structure
        for i, element in enumerate(elements[:3]):
            print(f"\nElement {i+1}:")
            print(f"  ID: {element.get('id')}")
            print(f"  Name: {element.get('name')}")
            print(f"  URL: {element.get('url')}")
            print(f"  ProductType: {element.get('productType')}")
            if 'partners' in element and element['partners']:
                print(f"  Partners: {[p.get('name') if isinstance(p, dict) else p for p in element['partners'][:2]]}")
            
        # Print full structure of the first element to understand what fields are available
        if elements:
            print(f"\nFull first element structure:")
            print(json.dumps(elements[0], indent=2, default=str)[:500] + "...")
            
    except Exception as e:
        print(f"Error in general search: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Test the domains that are failing
    failing_domains = ["computer-science", "business", "data-science"]
    working_domain = "health"
    
    print("Testing failing domains:")
    for domain in failing_domains:
        debug_domain_search(domain)
    
    print(f"\nTesting working domain:")
    debug_domain_search(working_domain)
    
    # Also try a general search to see the response structure
    debug_general_search()