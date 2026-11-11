"""Member Queries"""
from database.connection import get_db
from datetime import datetime
from logger import get_logger

log = get_logger("q.members")
db = get_db()

def bulk_insert(members: list, owner_id: str) -> int:
    if not members: return 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # تجهيز كل البيانات في مصفوفة واحدة
    data = []
    for m in members:
        data.append((m[0], m[1], m[2], m[3], m[4] if len(m) > 4 else now, str(owner_id)))
    
    try:
        with db.transaction():
            # حساب العدد قبل
            before = db.fetchone("SELECT COUNT(*) as c FROM members WHERE owner_user_id=?", (str(owner_id),))["c"]
            
            # استخدام executemany عشان يضيفهم كلهم مرة واحدة (فاست جداً ومش بيعمل لوك)
            db.executemany("INSERT OR IGNORE INTO members (id, username, user_id, scraped_from, scraped_at, owner_user_id) VALUES (?, ?, ?, ?, ?, ?)", data)
            
            # حساب العدد بعد
            after = db.fetchone("SELECT COUNT(*) as c FROM members WHERE owner_user_id=?", (str(owner_id),))["c"]
            return after - before
    except Exception as e:
        log.error(f"bulk_insert failed: {e}")
        return 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # تجهيز كل البيانات في مصفوفة واحدة
    data = []
    for m in members:
        data.append((m[0], m[1], m[2], m[3], m[4] if len(m) > 4 else now, str(owner_id)))
    
    try:
        with db.transaction():
            # حساب العدد قبل
            before = db.fetchone("SELECT COUNT(*) as c FROM members WHERE owner_user_id=?", (str(owner_id),))["c"]
            
            # استخدام executemany عشان يضيفهم كلهم مرة واحدة (فاست جداً ومش بيعمل لوك)
            db.executemany("INSERT OR IGNORE INTO members (id, username, user_id, scraped_from, scraped_at, owner_user_id) VALUES (?, ?, ?, ?, ?, ?)", data)
            
            # حساب العدد بعد
            after = db.fetchone("SELECT COUNT(*) as c FROM members WHERE owner_user_id=?", (str(owner_id),))["c"]
            return after - before
    except Exception as e:
        log.error(f"bulk_insert failed: {e}")
        return 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # تجهيز البيانات للـ executemany
    data = []
    for m in members:
        data.append((m[0], m[1], m[2], m[3], m[4] if len(m) > 4 else now, str(owner_id)))
    
    try:
        with db.transaction():
            # حساب العدد قبل الإضافة
            before = db.fetchone("SELECT COUNT(*) as c FROM members WHERE owner_user_id=?", (str(owner_id),))["c"]
            
            # إضافة الأعضاء (تجاهل المكرر)
            for row in data:
                db.execute("INSERT OR IGNORE INTO members (id, username, user_id, scraped_from, scraped_at, owner_user_id) VALUES (?, ?, ?, ?, ?, ?)", row)
            
            # حساب العدد بعد الإضافة
            after = db.fetchone("SELECT COUNT(*) as c FROM members WHERE owner_user_id=?", (str(owner_id),))["c"]
            
            # الفرق هو عدد الأعضاء الجدد اللي اتحفظوا
            return after - before
    except Exception as e:
        log.error(f"bulk_insert failed: {e}")
        return 0

def count(owner_id: str) -> int:
    row = db.fetchone("SELECT COUNT(*) as c FROM members WHERE owner_user_id=?", (str(owner_id),))
    return row["c"] if row else 0

def get_paginated(owner_id: str, limit: int = 50, offset: int = 0) -> list:
    rows = db.fetchall("SELECT * FROM members WHERE owner_user_id=? LIMIT ? OFFSET ?",
                       (str(owner_id), limit, offset))
    return [dict(r) for r in rows]

def deduplicate(owner_id: str) -> int:
    before = count(owner_id)
    db.execute("""DELETE FROM members WHERE rowid NOT IN (
        SELECT MIN(rowid) FROM members WHERE owner_user_id=? GROUP BY user_id
    ) AND owner_user_id=?""", (str(owner_id), str(owner_id)), commit=True)
    return before - count(owner_id)

def delete_member(member_id: str, owner_id: str) -> bool:
    db.execute("DELETE FROM members WHERE id=? AND owner_user_id=?", (member_id, str(owner_id)), commit=True)
    return True

def stats_by_owner(owner_id: str) -> dict:
    total = count(owner_id)
    with_username = db.fetchone("SELECT COUNT(*) as c FROM members WHERE owner_user_id=? AND username IS NOT NULL",
                                 (str(owner_id),))["c"]
    return {"total": total, "with_username": with_username, "without_username": total - with_username}
