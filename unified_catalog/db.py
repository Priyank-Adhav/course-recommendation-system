import sqlite3
from contextlib import contextmanager
from .config import TARGET_DB

PRAGMAS = [
    ("PRAGMA journal_mode=WAL;",),
    ("PRAGMA synchronous=NORMAL;",),
    ("PRAGMA foreign_keys=ON;",),
    ("PRAGMA temp_store=MEMORY;",),
    ("PRAGMA mmap_size=30000000000;",),  # 30GB if available; ignored if not
]

def open_conn(path=None) -> sqlite3.Connection:
    p = str(path or TARGET_DB)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    # Apply pragmas
    cur = conn.cursor()
    for (stmt,) in PRAGMAS:
        try:
            cur.execute(stmt)
        except Exception:
            pass
    conn.commit()
    return conn

@contextmanager
def transaction(conn: sqlite3.Connection):
    try:
        conn.execute("BEGIN")
        yield
        conn.commit()
    except Exception:
        conn.rollback()
        raise
