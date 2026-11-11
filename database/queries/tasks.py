"""Task/Wheel/Achievement Queries"""
import random
from datetime import datetime
from database.connection import get_db
from logger import get_logger

log = get_logger("q.tasks")
db = get_db()
def _now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def _today(): return datetime.now().strftime("%Y-%m-%d")

TASKS = {
    "t1": {"name": "اسحب 100 عضو", "reward": 20},
    "t2": {"name": "اضخ 50 عضو", "reward": 30},
    "t3": {"name": "العب عجلة الحظ", "reward": 15},
    "t4": {"name": "كلم المساعد", "reward": 10},
    "t5": {"name": "ارفع صورة", "reward": 25},
}

def get_daily(user_id: str) -> list:
    today = _today()
    done = {r["task_id"] for r in db.fetchall(
        "SELECT task_id FROM daily_tasks WHERE user_id=? AND date=?", (str(user_id), today))}
    return [{"id": k, "name": v["name"], "reward": v["reward"], "done": k in done}
            for k, v in TASKS.items()]

def claim(user_id: str, task_id: str) -> dict:
    if task_id not in TASKS: return {"ok": False, "error": "مهمة غير معروفة"}
    uid, today = str(user_id), _today()
    exists = db.fetchone("SELECT 1 FROM daily_tasks WHERE user_id=? AND task_id=? AND date=?",
                         (uid, task_id, today))
    if exists: return {"ok": False, "error": "استلمتها النهاردة"}
    reward = TASKS[task_id]["reward"]
    with db.transaction():
        db.execute("INSERT INTO daily_tasks (user_id, task_id, date, completed_at, claimed) VALUES (?, ?, ?, ?, 1)",
                   (uid, task_id, today, _now()))
        db.execute("UPDATE users SET points = points + ? WHERE id=?", (reward, uid))
    return {"ok": True, "reward": reward}

def wheel_spin(user_id: str) -> dict:
    uid, today = str(user_id), _today()
    row = db.fetchone("SELECT wheel_spins_today, last_wheel_date FROM users WHERE id=?", (uid,))
    if not row: return {"error": "مستخدم غير موجود"}
    spins = row["wheel_spins_today"] or 0
    if row["last_wheel_date"] != today: spins = 0
    if spins >= 3: return {"error": "وصلت للحد اليومي (3)"}
    # ترتيب متباعد للزيرو (مش جنب بعض)
    prizes = [0, 5, 0, 10, 20, 50, 100, 500]
    weights = [35, 15, 25, 10, 8, 4, 2, 1]
    idx = random.choices(range(len(prizes)), weights=weights, k=1)[0]
    won = prizes[idx]
    with db.transaction():
        db.execute("UPDATE users SET points = points + ?, wheel_spins_today=?, last_wheel_date=? WHERE id=?",
                   (won, spins + 1, today, uid))
    return {"won": won, "idx": idx, "spins_left": max(0, 3 - (spins + 1))}

def daily_box(user_id: str) -> dict:
    uid, today = str(user_id), _today()
    exists = db.fetchone("SELECT 1 FROM daily_box WHERE user_id=? AND date=?", (uid, today))
    if exists: return {"error": "فتحت الصندوق النهاردة"}
    reward = random.choices([10, 50, 100, 500, 1000], weights=[40, 30, 20, 9, 1])[0]
    with db.transaction():
        db.execute("INSERT INTO daily_box (user_id, date) VALUES (?, ?)", (uid, today))
        db.execute("UPDATE users SET points = points + ? WHERE id=?", (reward, uid))
    return {"ok": True, "reward": reward}


ACHIEVEMENTS_LIST = {
    "first_scrape": {"name": "أول سحب", "desc": "قم بعمل أول عملية سحب", "icon": "🥇", "reward": 50},
    "first_pump": {"name": "أول ضخ", "desc": "قم بعمل أول عملية ضخ", "icon": "🚀", "reward": 50},
    "scraped_100": {"name": "صياد محترف", "desc": "اسحب 100 عضو", "icon": "🎯", "reward": 100},
    "scraped_1000": {"name": "أسطورة السحب", "desc": "اسحب 1000 عضو", "icon": "🏆", "reward": 500},
    "points_1000": {"name": "ألفير", "desc": "اجمع 1000 نقطة", "icon": "💰", "reward": 100},
    "level_5": {"name": "المستوى الخامس", "desc": "اوصل للمستوى 5", "icon": "⭐", "reward": 200},
    "first_vip": {"name": "الملكي", "desc": "قم بشراء VIP", "icon": "👑", "reward": 150}
}

def check_achievements(user_id: str) -> list:
    uid = str(user_id)
    from database.queries import users as users_q
    user = users_q.get_user(uid)
    if not user: return []
    
    unlocked = set(get_achievements(uid))
    newly_unlocked = []
    
    total_scraped = user.get("total_scraped", 0) or 0
    total_pumped = user.get("total_pumped", 0) or 0
    points = user.get("points", 0) or 0
    level = user.get("level", 1) or 1
    role = user.get("role", "USER")
    
    to_check = {
        "first_scrape": total_scraped > 0,
        "first_pump": total_pumped > 0,
        "scraped_100": total_scraped >= 100,
        "scraped_1000": total_scraped >= 1000,
        "points_1000": points >= 1000,
        "level_5": level >= 5,
        "first_vip": role == "VIP"
    }
    
    for ach_id, condition in to_check.items():
        if condition and ach_id not in unlocked:
            unlock_achievement(uid, ach_id)
            reward = ACHIEVEMENTS_LIST[ach_id]["reward"]
            users_q.update_points(uid, reward)
            users_q.add_xp(uid, 50)
            newly_unlocked.append(ach_id)
            
    return newly_unlocked

def unlock_achievement(user_id: str, ach_id: str) -> bool:
    db.execute("INSERT OR IGNORE INTO user_achievements (user_id, achievement_id, unlocked_at) VALUES (?, ?, ?)",
               (str(user_id), ach_id, _now()), commit=True)
    return True

def get_achievements(user_id: str) -> list:
    rows = db.fetchall("SELECT achievement_id FROM user_achievements WHERE user_id=?", (str(user_id),))
    return [r["achievement_id"] for r in rows]
