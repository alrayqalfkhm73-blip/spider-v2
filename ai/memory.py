"""AI Memory — سياق + تصحيحات"""
from datetime import datetime
from database.connection import get_db
from logger import get_logger

log = get_logger("ai.memory")
db = get_db()

def ensure_tables():
    db.execute("""CREATE TABLE IF NOT EXISTS ai_context (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT,
        role TEXT, content TEXT, created_at TEXT
    )""", commit=True)
    db.execute("""CREATE TABLE IF NOT EXISTS ai_corrections (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT,
        original TEXT, correction TEXT, created_at TEXT
    )""", commit=True)

def save_message(user_id: str, role: str, content: str):
    ensure_tables()
    db.execute("INSERT INTO ai_context (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
               (str(user_id), role, content[:2000], datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
               commit=True)
    # Keep only last 20
    db.execute("""DELETE FROM ai_context WHERE id NOT IN (
        SELECT id FROM ai_context WHERE user_id=? ORDER BY id DESC LIMIT 20
    ) AND user_id=?""", (str(user_id), str(user_id)), commit=True)

def load_context(user_id: str, limit: int = 10) -> list:
    ensure_tables()
    rows = db.fetchall(
        "SELECT role, content FROM ai_context WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (str(user_id), limit)
    )
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

def save_correction(user_id: str, original: str, correction: str):
    ensure_tables()
    db.execute("INSERT INTO ai_corrections (user_id, original, correction, created_at) VALUES (?, ?, ?, ?)",
               (str(user_id), original[:300], correction[:300], datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
               commit=True)

def get_corrections(user_id: str, limit: int = 3) -> list:
    ensure_tables()
    rows = db.fetchall(
        "SELECT original, correction FROM ai_corrections WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (str(user_id), limit)
    )
    return [{"original": r["original"], "correction": r["correction"]} for r in rows]

def clear(user_id: str):
    ensure_tables()
    db.execute("DELETE FROM ai_context WHERE user_id=?", (str(user_id),), commit=True)
    db.execute("DELETE FROM ai_corrections WHERE user_id=?", (str(user_id),), commit=True)
