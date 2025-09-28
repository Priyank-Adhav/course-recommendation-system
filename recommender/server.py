from fastapi import FastAPI, Query
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from vector_store import warmup_system
from recommend import recommend


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
