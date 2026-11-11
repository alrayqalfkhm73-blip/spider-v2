"""User Queries"""
from datetime import datetime, timedelta
from database.connection import get_db
from database.cache import user_cache
from logger import get_logger

log = get_logger("q.users")
db = get_db()

def _now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_user(user_id: str) -> dict:
    uid = str(user_id)
    cached = user_cache.get(f"user:{uid}")
    if cached: return cached
    row = db.fetchone("SELECT * FROM users WHERE id=?", (uid,))
    if row:
        d = dict(row)
        user_cache.set(f"user:{uid}", d)
        return d
    return None

def ensure_user(user_id: str) -> dict:
    uid = str(user_id)
    user = get_user(uid)
    if user: return user
    db.execute("INSERT OR IGNORE INTO users (id, joined_at) VALUES (?, ?)", (uid, _now()), commit=True)
    user_cache.invalidate(f"user:{uid}")
    return get_user(uid)

def update_points(user_id: str, delta: int) -> int:
    from config import config
    uid = str(user_id)
    if uid == str(config.telegram.owner_id):
        return 999999999 # المالك لا يخصم منه أبداً
    
    ensure_user(uid)
    with db.transaction():
        db.execute("UPDATE users SET points = MAX(0, points + ?) WHERE id=?", (delta, uid))
        row = db.fetchone("SELECT points FROM users WHERE id=?", (uid,))
    user_cache.invalidate(f"user:{uid}")
    return row["points"] if row else 0

def set_role(user_id: str, role: str, vip_days: int = 0) -> bool:
    uid = str(user_id)
    ensure_user(uid)
    expiry = None
    if vip_days > 0:
        expiry = (datetime.now() + timedelta(days=vip_days)).strftime("%Y-%m-%d %H:%M:%S")
    db.execute("UPDATE users SET role=?, vip_expiry=? WHERE id=?", (role, expiry, uid), commit=True)
    user_cache.invalidate(f"user:{uid}")
    return True

def is_vip(user_id: str) -> bool:
    user = get_user(user_id)
    if not user or user.get("role") != "VIP":
        return False
    exp = user.get("vip_expiry")
    if exp and exp < _now():
        set_role(user_id, "USER", 0)
        return False
    return True

def ban_user(user_id: str, reason: str = "admin", days: int = 0) -> bool:
    uid = str(user_id)
    expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S") if days > 0 else None
    db.execute("INSERT OR REPLACE INTO banned (id, reason, banned_at, ban_expires) VALUES (?, ?, ?, ?)",
               (uid, reason, _now(), expiry), commit=True)
    db.execute("UPDATE users SET ban_reason=? WHERE id=?", (reason, uid), commit=True)
    user_cache.invalidate(f"user:{uid}")
    return True

def unban_user(user_id: str) -> bool:
    uid = str(user_id)
    db.execute("DELETE FROM banned WHERE id=?", (uid,), commit=True)
    db.execute("UPDATE users SET ban_reason=NULL WHERE id=?", (uid,), commit=True)
    user_cache.invalidate(f"user:{uid}")
    return True

def is_banned(user_id: str) -> bool:
    uid = str(user_id)
    row = db.fetchone("SELECT ban_expires FROM banned WHERE id=?", (uid,))
    if not row: return False
    exp = row["ban_expires"]
    if exp and exp < _now():
        unban_user(uid)
        return False
    return True

def get_top_users(limit: int = 10) -> list:
    rows = db.fetchall("SELECT id, points, role FROM users ORDER BY points DESC LIMIT ?", (limit,))
    return [dict(r) for r in rows]

def increment_stat(user_id: str, field: str, amount: int = 1):
    if field not in ("total_scraped", "total_pumped", "referral_count"):
        return False
    uid = str(user_id)
    db.execute(f"UPDATE users SET {field} = {field} + ? WHERE id=?", (amount, uid), commit=True)
    user_cache.invalidate(f"user:{uid}")
    return True


def check_streak(user_id: str) -> dict:
    uid = str(user_id)
    user = get_user(uid)
    if not user: return {"streak": 0, "reward": 0}
    
    from datetime import datetime, timedelta
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    last_date = user.get("last_gift_date")
    streak = user.get("gift_streak", 0) or 0
    reward = 0
    
    if last_date == today:
        return {"streak": streak, "reward": 0, "already": True}
        
    if last_date == yesterday:
        streak += 1
    else:
        streak = 1 # بداية ستريك جديد
        
    streak = min(streak, 7) # الحد الأقصى 7 أيام
    reward = streak * 10 # 10, 20, 30... 70 نقطة
    
    with db.transaction():
        db.execute("UPDATE users SET gift_streak=?, last_gift_date=? WHERE id=?", (streak, today, uid))
        db.execute("UPDATE users SET points = points + ? WHERE id=?", (reward, uid))
        
    user_cache.invalidate(f"user:{uid}")
    return {"streak": streak, "reward": reward, "already": False}


def add_xp(user_id: str, amount: int) -> dict:
    uid = str(user_id)
    ensure_user(uid)
    with db.transaction():
        db.execute("UPDATE users SET xp = xp + ? WHERE id=?", (amount, uid))
        row = db.fetchone("SELECT xp, level FROM users WHERE id=?", (uid,))
        
        if row:
            current_xp = row["xp"]
            current_level = row["level"]
            new_level = (current_xp // 100) + 1 # كل 100 نقطة = مستوى
            
            if new_level > current_level:
                db.execute("UPDATE users SET level = ? WHERE id=?", (new_level, uid))
                db.execute("UPDATE users SET points = points + 100 WHERE id=?", (uid,)) # مكافأة الترقية
                user_cache.invalidate(f"user:{uid}")
                return {"level_up": True, "new_level": new_level}
                
    user_cache.invalidate(f"user:{uid}")
    return {"level_up": False}

def get_summary(user_id: str) -> dict:
    user = get_user(user_id)
    if not user: return {}
    return {
        "id": user["id"],
        "points": user.get("points", 0),
        "role": user.get("role", "USER"),
        "is_vip": is_vip(user_id),
        "is_banned": is_banned(user_id),
        "total_scraped": user.get("total_scraped", 0),
        "total_pumped": user.get("total_pumped", 0),
        "referrals": user.get("referral_count", 0),
    }
