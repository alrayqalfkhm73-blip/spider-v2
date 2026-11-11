"""Log Queries"""
from datetime import datetime, timedelta
from database.connection import get_db

db = get_db()
def _now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_event(event_type: str, message: str) -> bool:
    db.execute("INSERT INTO logs (event_type, message, created_at) VALUES (?, ?, ?)",
               (event_type, message[:500], _now()), commit=True)
    return True

def log_activity(user_id: str, action: str, details: str = "", admin_id: str = "") -> bool:
    db.execute("INSERT INTO activity_log (user_id, action, details, admin_id, created_at) VALUES (?, ?, ?, ?, ?)",
               (str(user_id), action, details[:300], str(admin_id), _now()), commit=True)
    return True

def cleanup_old(days: int = 30) -> int:
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    cur1 = db.execute("DELETE FROM logs WHERE created_at < ?", (cutoff,), commit=True)
    cur2 = db.execute("DELETE FROM activity_log WHERE created_at < ?", (cutoff,), commit=True)
    return cur1.rowcount + cur2.rowcount

def get_recent_logs(limit: int = 20) -> list:
    rows = db.fetchall("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,))
    return [dict(r) for r in rows]
