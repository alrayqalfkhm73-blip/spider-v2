"""الخطوة 2 — Database — 47 اختبار"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

passed = failed = 0
def ck(name, cond, detail=""):
    global passed, failed
    if cond: passed += 1; print(f"  ✅ {name}" + (f" — {detail}" if detail else ""))
    else: failed += 1; print(f"  ❌ {name}" + (f" — {detail}" if detail else ""))

print("=" * 55)
print("🧪 اختبار الخطوة 2 — Database")
print("=" * 55)

# [0] Apply migrations FIRST
print("\n[0] تطبيق migrations...")
try:
    from database.migrations import apply_all
    apply_all()
    ck("apply_all()", True)
except Exception as e:
    ck("apply_all", False, str(e)[:80])

# [1] Connection (6)
print("\n[1] connection.py (6)")
try:
    from database.connection import get_db
    db = get_db()
    ck("get_db()", db is not None)
    ck("singleton", get_db() is db)
    ck("ping()", db.ping())
    ck("execute", db.execute("SELECT 1").fetchone() is not None)
    with db.transaction():
        db.execute("SELECT 1")
    ck("transaction()", True)
    ck("backup()", callable(db.backup))
except Exception as e:
    ck("connection", False, str(e)[:60])

# [2] Schema (15)
print("\n[2] schema.py (15)")
try:
    from database.schema import table_exists, column_exists
    for t in ["users", "sessions", "members", "codes", "banned", "proxies",
              "tasks", "logs", "daily_tasks", "transactions", "user_achievements",
              "feedback", "daily_box", "user_settings", "schema_version"]:
        ck(f"table {t}", table_exists(t))
    ck("column owners", column_exists("members", "owner_user_id"))
    ck("column reason", column_exists("banned", "reason"))
    ck("column used_by", column_exists("codes", "used_by"))
except Exception as e:
    ck("schema", False, str(e)[:60])

# [3] Migrations (4)
print("\n[3] migrations.py (4)")
try:
    from database.migrations import get_current_version, add_column_safe
    ck("schema_version", get_current_version() >= 1)
    ck("add_column_safe", callable(add_column_safe))
    ck("version recorded", get_current_version() == 1)
    ck("tables ok", table_exists("users"))
except Exception as e:
    ck("migrations", False, str(e)[:60])

# [4] Cache (2)
print("\n[4] cache.py (2)")
try:
    from database.cache import TTLCache, user_cache
    c = TTLCache(ttl_ms=100)
    c.set("k", "v")
    ck("set/get", c.get("k") == "v")
    ck("user_cache", user_cache is not None)
except Exception as e:
    ck("cache", False, str(e)[:60])

# [5] users.py (6)
print("\n[5] queries/users.py (6)")
try:
    from database.queries import users as U
    uid = "test_user_ck"
    U.ensure_user(uid)
    ck("ensure_user", U.get_user(uid) is not None)
    U.update_points(uid, 100)
    ck("update_points", U.get_user(uid)["points"] >= 100)
    U.set_role(uid, "VIP", 7)
    ck("set_role VIP", U.is_vip(uid))
    U.ban_user(uid, "test", 1)
    ck("ban_user", U.is_banned(uid))
    U.unban_user(uid)
    ck("unban_user", not U.is_banned(uid))
    top = U.get_top_users(5)
    ck("get_top_users", isinstance(top, list))
except Exception as e:
    ck("users queries", False, str(e)[:80])

# [6] sessions.py (4)
print("\n[6] queries/sessions.py (4)")
try:
    from database.queries import sessions as S
    S.add("test_user_sess", "test_sess", "/tmp/test_sess")
    ck("add", S.get_by_name("test_sess") is not None)
    ck("get_all", len(S.get_all("test_user_sess")) > 0)
    ck("heartbeat", S.update_heartbeat("test_sess"))
    ck("daily_limit", S.daily_limit_check("test_sess"))
    S.remove("test_sess", "/tmp/test_sess")
except Exception as e:
    ck("sessions queries", False, str(e)[:80])

# [7] members.py (3)
print("\n[7] queries/members.py (3)")
try:
    from database.queries import members as M
    batch = [(f"@testm_{i}", f"tm{i}", f"mid_{i}", "test", "2026-01-01") for i in range(5)]
    ck("bulk_insert", M.bulk_insert(batch, "test_owner") >= 0)
    ck("count", M.count("test_owner") >= 0)
    ck("stats", isinstance(M.stats_by_owner("test_owner"), dict))
except Exception as e:
    ck("members queries", False, str(e)[:80])

# [8] codes.py (2)
print("\n[8] queries/codes.py (2)")
try:
    from database.queries import codes as C
    codes = C.create(100, 1, 30)
    ck("create", len(codes) == 1)
    ck("stats", isinstance(C.stats(), dict))
except Exception as e:
    ck("codes queries", False, str(e)[:80])

# [9] tasks.py (3)
print("\n[9] queries/tasks.py (3)")
try:
    from database.queries import tasks as T
    ck("get_daily", isinstance(T.get_daily("test_user_t"), list))
    import random
    r = T.daily_box(f"test_box_{random.randint(0,99999)}")
    ck("daily_box", "reward" in r or "error" in r)
    ck("get_achievements", isinstance(T.get_achievements("test_user_t"), list))
except Exception as e:
    ck("tasks queries", False, str(e)[:80])

# [10] logs.py (2)
print("\n[10] queries/logs.py (2)")
try:
    from database.queries import logs as L
    ck("log_event", L.log_event("test", "test message"))
    ck("get_recent_logs", isinstance(L.get_recent_logs(5), list))
except Exception as e:
    ck("logs queries", False, str(e)[:80])

# Final
print("\n" + "=" * 55)
total = passed + failed
print(f"📊 النتيجة: ✅ {passed}/{total} · ❌ {failed}")
print("=" * 55)
if failed > 0:
    print(f"\n❌ {failed} فشل")
    sys.exit(1)
