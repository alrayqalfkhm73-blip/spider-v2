"""Session Queries"""
from datetime import datetime
from database.connection import get_db
from logger import get_logger

log = get_logger("q.sessions")
db = get_db()
def _now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def add(user_id: str, name: str, path: str) -> bool:
    db.execute("INSERT OR REPLACE INTO sessions (user_id, session_name, session_path, added_at, status) VALUES (?, ?, ?, ?, 'ACTIVE')",
               (str(user_id), name, path, _now()), commit=True)
    return True

def get_all(user_id: str) -> list:
    rows = db.fetchall("SELECT * FROM sessions WHERE user_id=?", (str(user_id),))
    return [dict(r) for r in rows]

def get_active(user_id: str) -> dict:
    row = db.fetchone("SELECT * FROM sessions WHERE user_id=? AND status='ACTIVE' LIMIT 1", (str(user_id),))
    return dict(row) if row else None

def get_by_name(name: str) -> dict:
    row = db.fetchone("SELECT * FROM sessions WHERE session_name=?", (name,))
    return dict(row) if row else None

def update_heartbeat(name: str) -> bool:
    db.execute("UPDATE sessions SET last_used=? WHERE session_name=?", (_now(), name), commit=True)
    return True

def increment_pump(name: str) -> bool:
    today = datetime.now().strftime("%Y-%m-%d")
    with db.transaction():
        # لو التاريخ اتغير، بنصفر العداد ونبدأ من 1
        db.execute("""
            UPDATE sessions 
            SET pump_count = pump_count + 1, 
                daily_pumped = CASE WHEN last_pump_date = ? THEN daily_pumped + 1 ELSE 1 END, 
                last_pump_date = ? 
            WHERE session_name = ?
        """, (today, today, name))
    return True


def increment_scrape(name: str) -> bool:
    db.execute("UPDATE sessions SET scrape_count = scrape_count + 1 WHERE session_name = ?", (name,), commit=True)
    return True

def daily_limit_check(name: str, limit: int = 20) -> bool:
    today = datetime.now().strftime("%Y-%m-%d")
    row = db.fetchone("SELECT daily_pumped, last_pump_date FROM sessions WHERE session_name=?", (name,))
    if not row: return True
    if row["last_pump_date"] != today: return True
    return row["daily_pumped"] < limit

def remove(name: str, file_path: str = None) -> bool:
    db.execute("DELETE FROM sessions WHERE session_name=?", (name,), commit=True)
    if file_path:
        import os
        for suffix in ["", "-journal", "-wal", "-shm"]:
            try: os.remove(file_path + suffix)
            except: pass
    return True
