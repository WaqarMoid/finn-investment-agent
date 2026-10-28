import os
import sqlite3
from pathlib import Path
from typing import Optional

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def get_db_path() -> str:
    data_dir = os.getenv("DATA_DIR", "./data")
    os.makedirs(data_dir, exist_ok=True)
    return os.getenv("DATABASE_PATH", os.path.join(data_dir, "finn.db"))

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    target_path = db_path or get_db_path()
    conn = sqlite3.connect(target_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    return conn

def init_db(db_path: Optional[str] = None) -> None:
    conn = get_connection(db_path)
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            ddl = f.read()
        conn.executescript(ddl)
        conn.commit()
    finally:
        conn.close()
