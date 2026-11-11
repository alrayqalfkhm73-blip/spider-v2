"""Progress Tracking — يخلي الواجهة تشوف التقدم"""
import uuid
from datetime import datetime, timedelta
from database.connection import get_db
from logger import get_logger

log = get_logger("scraper.progress")
db = get_db()

def ensure_table():
    db.execute("""CREATE TABLE IF NOT EXISTS scrape_progress (
        task_id TEXT PRIMARY KEY,
        user_id TEXT,
        kind TEXT,
        target TEXT,
        status TEXT DEFAULT 'pending',
        scraped INTEGER DEFAULT 0,
        scanned INTEGER DEFAULT 0,
        failed INTEGER DEFAULT 0,
        reason TEXT,
        members_preview TEXT,
        started_at TEXT,
        updated_at TEXT
    )""", commit=True)

def create(kind: str, user_id: str, target: str) -> str:
    ensure_table()
    task_id = str(uuid.uuid4())[:12]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "INSERT INTO scrape_progress (task_id, user_id, kind, target, status, started_at, updated_at) VALUES (?, ?, ?, ?, 'running', ?, ?)",
        (task_id, str(user_id), kind, target, now, now), commit=True
    )
    log.info(f"Task {task_id} created: {kind}")
    return task_id

def update(task_id: str, **kwargs):
    if not kwargs: return
    fields = ", ".join(f"{k}=?" for k in kwargs.keys())
    values = list(kwargs.values()) + [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id]
    db.execute(f"UPDATE scrape_progress SET {fields}, updated_at=? WHERE task_id=?",
               tuple(values), commit=True)

def increment(task_id: str, field: str, amount: int = 1):
    if field not in ("scraped", "scanned", "failed"): return
    db.execute(f"UPDATE scrape_progress SET {field}={field}+?, updated_at=? WHERE task_id=?",
               (amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id), commit=True)

def get(task_id: str) -> dict:
    ensure_table()
    row = db.fetchone("SELECT * FROM scrape_progress WHERE task_id=?", (task_id,))
    return dict(row) if row else None

def cancel(task_id: str):
    update(task_id, status="cancelled")

def finish(task_id: str, status: str = "completed"):
    update(task_id, status=status)

def cleanup_old(days: int = 1) -> int:
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    cur = db.execute("DELETE FROM scrape_progress WHERE started_at < ?", (cutoff,), commit=True)
    return cur.rowcount

def user_active_tasks(user_id: str) -> list:
    ensure_table()
    rows = db.fetchall(
        "SELECT task_id FROM scrape_progress WHERE user_id=? AND status='running'",
        (str(user_id),)
    )
    return [r["task_id"] for r in rows]


def update_members_preview(task_id: str, members_list: list):
    """يحفظ آخر 10 أعضاء (JSON)"""
    import json
    try:
        db.execute(
            "UPDATE scrape_progress SET members_preview=?, updated_at=? WHERE task_id=?",
            (json.dumps(members_list, ensure_ascii=False), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id),
            commit=True
        )
    except Exception as e:
        log.debug(f"update_members_preview failed: {e}")

