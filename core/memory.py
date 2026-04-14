"""
Synapse Studio V2 Ultra – Persistent Memory Layer
ChromaDB (vector) + SQLite (sessions + messages)
"""
import json
import time
import uuid
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any

import chromadb
from chromadb.config import Settings

# ─── Paths ────────────────────────────────────────────────────────────────────
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH   = DATA_DIR / "synapse.db"
CHROMA_DIR = DATA_DIR / "chroma"


# ─── SQLite session store ──────────────────────────────────────────────────────

def _get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id          TEXT PRIMARY KEY,
                name        TEXT,
                mode        TEXT,
                prompt      TEXT,
                created_at  REAL,
                updated_at  REAL,
                status      TEXT DEFAULT 'running',
                summary     TEXT
            );
            CREATE TABLE IF NOT EXISTS messages (
                id          TEXT PRIMARY KEY,
                session_id  TEXT,
                agent       TEXT,
                emoji       TEXT,
                content     TEXT,
                iteration   INTEGER DEFAULT 0,
                score       REAL,
                timestamp   REAL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
            CREATE TABLE IF NOT EXISTS scores (
                id                  TEXT PRIMARY KEY,
                session_id          TEXT,
                iteration           INTEGER,
                technical           REAL,
                scalability         REAL,
                innovation          REAL,
                business_value      REAL,
                code_quality        REAL,
                overall             REAL,
                timestamp           REAL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
        """)


def create_session(name: str, prompt: str, mode: str = "build") -> str:
    sid = str(uuid.uuid4())
    now = time.time()
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO sessions VALUES (?,?,?,?,?,?,?,?)",
            (sid, name, mode, prompt, now, now, "running", None)
        )
    return sid


def update_session(session_id: str, **kwargs):
    kwargs["updated_at"] = time.time()
    cols = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [session_id]
    with _get_conn() as conn:
        conn.execute(f"UPDATE sessions SET {cols} WHERE id=?", vals)


def save_message(session_id: str, agent: str, emoji: str, content: str,
                 iteration: int = 0, score: Optional[float] = None):
    mid = str(uuid.uuid4())
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO messages VALUES (?,?,?,?,?,?,?,?)",
            (mid, session_id, agent, emoji, content, iteration, score, time.time())
        )


def save_score(session_id: str, iteration: int, scores: Dict[str, float]):
    sid = str(uuid.uuid4())
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO scores VALUES (?,?,?,?,?,?,?,?,?,?)",
            (sid, session_id, iteration,
             scores.get("technical_complexity", 0),
             scores.get("scalability", 0),
             scores.get("innovation", 0),
             scores.get("business_value", 0),
             scores.get("code_quality", 0),
             scores.get("overall", 0),
             time.time())
        )


def list_sessions() -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY updated_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_session_messages(session_id: str) -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE session_id=? ORDER BY timestamp ASC",
            (session_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_session_scores(session_id: str) -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM scores WHERE session_id=? ORDER BY iteration ASC",
            (session_id,)
        ).fetchall()
    return [dict(r) for r in rows]


# ─── ChromaDB vector memory ────────────────────────────────────────────────────

def _chroma_client():
    return chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )


def _collection(name: str = "synapse_memory"):
    client = _chroma_client()
    return client.get_or_create_collection(name)


def store_memory(session_id: str, agent: str, content: str, metadata: dict = None):
    """Store an agent message in vector memory."""
    col = _collection()
    doc_id = f"{session_id}_{agent}_{int(time.time()*1000)}"
    col.add(
        ids=[doc_id],
        documents=[content],
        metadatas=[{"session_id": session_id, "agent": agent, **(metadata or {})}],
    )


def recall_memory(query: str, n_results: int = 5, session_id: str = None) -> List[str]:
    """Retrieve semantically similar past memories."""
    col = _collection()
    where = {"session_id": session_id} if session_id else None
    try:
        results = col.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )
        return results["documents"][0] if results["documents"] else []
    except Exception:
        return []


# Auto-init
init_db()
