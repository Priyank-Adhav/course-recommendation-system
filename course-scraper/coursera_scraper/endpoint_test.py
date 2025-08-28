import requests
import json

# URL for Coursera's GraphQL search
url = "https://www.coursera.org/graphql-gateway?opname=Search"

# The query you captured, modified to fetch more courses (e.g., limit=50 instead of 1/12)
payload = [
    {
        "operationName": "Search",
        "variables": {
            "requests": [
                {
                    "entityType": "PRODUCTS",
                    "limit": 1500,  # number of courses you want
                    "disableRecommender": True,
                    "maxValuesPerFacet": 1000,
                    "facetFilters": [],
                    "cursor": "0",
                    "query": "computer science"  # empty string means all courses, add keyword to search (e.g., "IT")
                },
                {
                    "entityType": "SUGGESTIONS",
                    "limit": 7,
                    "disableRecommender": True,
                    "maxValuesPerFacet": 1000,
                    "facetFilters": [],
                    "cursor": "0",
                    "query": ""
                }
            ]
        },
        "query": """query Search($requests: [Search_Request!]!) {
          SearchResult {
            search(requests: $requests) {
              elements {
                ...SearchProductHit
              }
              pagination {
                cursor
                totalElements
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
        }"""
    }
]

# Headers (keep minimal, only what’s needed)
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# Make the request
response = requests.post(url, headers=headers, json=payload)

# Save output to a file
output_file = "coursera_courses.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(response.json(), f, indent=2, ensure_ascii=False)

print(f"Saved response to {output_file}")
