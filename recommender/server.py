from fastapi import FastAPI, Query, HTTPException
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from vector_store import warmup_system
from recommend import recommend
from user_recommendations import generate_user_recommendations

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    warmup_system()
    yield
    # Shutdown (if needed, e.g. closing db connections)


app = FastAPI(
    title="Course Recommendation API",
    description="Hybrid Content-based Recommendation System for Courses",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/recommend", response_model=List[Dict[str, Any]])
def get_recommendations(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(10, description="Number of recommendations to return")
):
    """
    Returns top-k course recommendations for a given query.
    """
    results = recommend(query, top_k=top_k)
    return results

@app.get("/recommend/{user_id}")
def recommend_for_user(user_id: int):
    try:
        recommendations = generate_user_recommendations(user_id)
        return {
            "struggled_section": {
                "title": "You struggled with these topics — here are some helpful courses",
                "courses": recommendations.get("struggled", [])
            },
            "strong_section": {
                "title": "You performed well in these areas — try these advanced-level courses",
                "courses": recommendations.get("strong", [])
            },
            "interest_section": {
                "title": "You’ve shown interest in these topics — you might like these courses",
                "courses": recommendations.get("interest", [])
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))