import time
import faiss
from vector_store import OptimizedVectorStore

def recommend(query: str, top_k: int = 10):
    start_time = time.time()
    
    store = OptimizedVectorStore()
    model = store.get_model()
    index, course_ids = store.get_index_and_ids()
    course_cache = store.get_course_cache()
    
    query_vec = model.encode(
        [query], convert_to_numpy=True,
        show_progress_bar=False, batch_size=1
    )
    faiss.normalize_L2(query_vec)
    
    D, I = index.search(query_vec, top_k)
    
    results = []
    for idx, score in zip(I[0], D[0]):
        if idx == -1:
            continue
        cid = str(course_ids[idx])
        if cid in course_cache:
            c = course_cache[cid]
            url = c["url"] or ""

            # Temporary Coursera URL patch
            if url.startswith("/"):
                url = f"https://www.coursera.org{url}"

            results.append({
                "course_id": cid,
                "title": c["title"],
                "url": url,
                "provider": c["provider"],
                "level": c["level"],
                "score": float(score)
            })

    print(f"Query '{query}' done in {time.time() - start_time:.3f}s")
    return results



if __name__ == "__main__":
    queries = ["python programming", "machine learning", "web development", "data science"]
    for q in queries:
        results = recommend(q, top_k=3)
        print(f"\nTop results for '{q}':")
        for r in results:
            print(f" - {r['title']} ({r['provider']}, score {r['score']:.3f})")
