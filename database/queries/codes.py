"""Code Queries — مع logging للأخطاء"""
import random
from datetime import datetime, timedelta
from database.connection import get_db
from database.schema import column_exists
from logger import get_logger

log = get_logger("q.codes")
db = get_db()
def _now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# الأعمدة المطلوبة (لو ناقصة، نضيفها)
REQUIRED_COLS = {
    "value": "INTEGER DEFAULT 0",
    "created_at": "TEXT",
    "expires_at": "TEXT",
    "max_uses": "INTEGER DEFAULT 1",
    "current_uses": "INTEGER DEFAULT 0",
    "type": "TEXT DEFAULT 'VIP'",
    "used_by": "TEXT",
    "used_at": "TEXT",
}

def _ensure_columns():
    """يتأكد من وجود كل الأعمدة المطلوبة"""
    for col, typ in REQUIRED_COLS.items():
        if not column_exists("codes", col):
            try:
                db.execute(f"ALTER TABLE codes ADD COLUMN {col} {typ}", commit=True)
                log.info(f"Added codes.{col}")
            except Exception as e:
                log.warning(f"Add codes.{col}: {e}")

def create(value: int, count: int = 1, days: int = 30) -> list:
    _ensure_columns()
    expires = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S") if days > 0 else None
    codes = []
    for _ in range(count):
        for attempt in range(5):  # retry على collision
            code = f"SPIDER_{random.randint(100000, 999999)}"
            try:
                db.execute(
                    "INSERT INTO codes (code, value, created_at, expires_at, max_uses, current_uses) "
                    "VALUES (?, ?, ?, ?, 1, 0)",
                    (code, value, _now(), expires),
                    commit=True
                )
                codes.append(code)
                break
            except Exception as e:
                err = str(e).upper()
                if "UNIQUE" in err or "PRIMARY KEY" in err:
                    log.debug(f"Code collision, retry {attempt+1}/5")
                    continue
                log.error(f"Codes insert failed: {e}")
                break
    log.info(f"Created {len(codes)}/{count} codes")
    return codes

def redeem(code: str, user_id: str) -> dict:
    code = code.strip().upper()
    row = db.fetchone("SELECT * FROM codes WHERE code=?", (code,))
    if not row: return {"ok": False, "error": "كود غير صحيح"}
    if row["used_by"]: return {"ok": False, "error": "الكود مستخدم"}
    if row["expires_at"] and row["expires_at"] < _now():
        return {"ok": False, "error": "الكود منتهي"}
    if (row["current_uses"] or 0) >= (row["max_uses"] or 1):
        return {"ok": False, "error": "الكود استُنفد"}
    new_uses = (row["current_uses"] or 0) + 1
    used_by = str(user_id) if new_uses >= (row["max_uses"] or 1) else None
    with db.transaction():
        db.execute("UPDATE codes SET current_uses=?, used_by=?, used_at=? WHERE code=?",
                   (new_uses, used_by, _now(), code))
        db.execute("INSERT OR IGNORE INTO users (id, joined_at) VALUES (?, ?)", (str(user_id), _now()))
        db.execute("UPDATE users SET points = points + ? WHERE id=?", (row["value"], str(user_id)))
    return {"ok": True, "value": row["value"]}

def expire_old() -> int:
    cur = db.execute("DELETE FROM codes WHERE expires_at IS NOT NULL AND expires_at < ?", (_now(),), commit=True)
    return cur.rowcount

def stats() -> dict:
    try:
        total = db.fetchone("SELECT COUNT(*) as c FROM codes")["c"]
        used = db.fetchone("SELECT COUNT(*) as c FROM codes WHERE used_by IS NOT NULL")["c"]
        return {"total": total, "used": used, "available": total - used}
    except Exception as e:
        log.error(f"stats: {e}")
        return {"total": 0, "used": 0, "available": 0}

def delete(code: str) -> bool:
    db.execute("DELETE FROM codes WHERE code=?", (code,), commit=True)
    return True
