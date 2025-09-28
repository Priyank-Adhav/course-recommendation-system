import sqlite3
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import logging
import time
from config import DB_PATH, INDEX_PATH, EMBEDDING_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedVectorStore:
    """Singleton pattern for model and data caching"""
    _instance = None
    _model = None
    _index = None
    _course_ids = None
    _course_cache = None  # Cache full course data
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_model(cls):
        if cls._model is None:
            logger.info(f"Loading model: {EMBEDDING_MODEL}")
            start_time = time.time()
            cls._model = SentenceTransformer(EMBEDDING_MODEL)
            cls._model.eval()
            logger.info(f"Model loaded in {time.time() - start_time:.2f}s")
        return cls._model
    
    @classmethod
    def get_index_and_ids(cls):
        if cls._index is None or cls._course_ids is None:
            logger.info("Loading FAISS index and course IDs")
            start_time = time.time()
            cls._index = faiss.read_index(str(INDEX_PATH))
            cls._course_ids = np.load(str(INDEX_PATH) + "_ids.npy", allow_pickle=True)
            logger.info(f"Index loaded in {time.time() - start_time:.3f}s")
        return cls._index, cls._course_ids
    
    @classmethod
    def get_course_cache(cls):
        if cls._course_cache is None:
            logger.info("Building course data cache")
            start_time = time.time()
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT course_id, title, url, provider, level FROM unified_courses")
            rows = cur.fetchall()
            conn.close()
            
            cls._course_cache = {
                str(row[0]): {
                    "title": row[1],
                    "url": row[2],
                    "provider": row[3],
                    "level": row[4]
                }
                for row in rows
            }
            logger.info(f"Course cache built in {time.time() - start_time:.3f}s with {len(cls._course_cache)} courses")
        return cls._course_cache


def build_optimized_index():
    print(f"🔹 Building optimized index with model: {EMBEDDING_MODEL}")
    
    model = SentenceTransformer(EMBEDDING_MODEL)
    dim = model.get_sentence_embedding_dimension()
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT course_id, title, tags FROM course_features")
    rows = cur.fetchall()
    conn.close()
    
    course_ids, texts = [], []
    for cid, title, tags in rows:
        title_clean = (title or "").strip()
        tags_clean = (tags or "").strip()
        text = f"{title_clean}. {tags_clean}".strip()
        texts.append(text)
        course_ids.append(cid)
    
    print(f"Processing {len(texts)} courses...")
    
    embeddings = model.encode(
        texts, convert_to_numpy=True,
        show_progress_bar=True, batch_size=32
    )
    
    index = faiss.IndexFlatIP(dim)
    if faiss.get_num_gpus() > 0 and len(course_ids) > 1000:
        print("🚀 Using GPU acceleration for index")
        gpu_index = faiss.index_cpu_to_gpu(faiss.StandardGpuResources(), 0, index)
        faiss.normalize_L2(embeddings)
        gpu_index.add(embeddings)
        index = faiss.index_gpu_to_cpu(gpu_index)
    else:
        faiss.normalize_L2(embeddings)
        index.add(embeddings)
    
    faiss.write_index(index, str(INDEX_PATH))
    np.save(str(INDEX_PATH) + "_ids.npy", np.array(course_ids))
    
    print(f"✅ Built optimized FAISS index → {INDEX_PATH}")
    return index, course_ids


def warmup_system():
    print("🔥 Warming up recommendation system...")
    start_time = time.time()
    
    store = OptimizedVectorStore()
    store.get_model()
    store.get_index_and_ids()
    store.get_course_cache()
    
    from recommend import recommend
    recommend("test query", top_k=5)
    
    print(f"✅ System warmed up in {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    build_optimized_index()
