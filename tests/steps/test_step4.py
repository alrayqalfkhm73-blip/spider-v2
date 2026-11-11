"""Step 4 — Flask Web — 35+ tests"""
import sys, asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    asyncio.get_running_loop()
except RuntimeError:
    try: asyncio.get_event_loop()
    except RuntimeError: asyncio.set_event_loop(asyncio.new_event_loop())

passed = failed = 0
def ck(name, cond, detail=""):
    global passed, failed
    if cond: passed += 1; print(f"  ✅ {name}" + (f" — {detail}" if detail else ""))
    else: failed += 1; print(f"  ❌ {name}" + (f" — {detail}" if detail else ""))

print("=" * 55)
print("🧪 اختبار الخطوة 4 — Flask Web")
print("=" * 55)

# Apply migrations
from database.migrations import apply_all
apply_all()

# [1] Imports (7)
print("\n[1] Imports (7)")
try:
    from web.app import create_app, app
    ck("web.app", True)
except Exception as e: ck("web.app", False, str(e)[:60])

try:
    from web.auth import hash_password, verify_login, get_session_user
    ck("web.auth", True)
except Exception as e: ck("web.auth", False, str(e)[:60])

try:
    from web.deps import require_login, require_owner, get_uid
    ck("web.deps", True)
except Exception as e: ck("web.deps", False, str(e)[:60])

try:
    from web.routes import register_routes
    ck("web.routes", True)
except Exception as e: ck("web.routes", False, str(e)[:60])

try:
    from web.routes import auth, me, health
    ck("blueprints", True)
except Exception as e: ck("blueprints", False, str(e)[:60])

try:
    ck("app instance", app is not None)
    ck("secret key", bool(app.secret_key))
except Exception as e: ck("app config", False, str(e)[:60])

# [2] Auth Logic (6)
print("\n[2] Auth logic (6)")
try:
    from web.auth import hash_password as hp, verify_login as vl
    ck("hash_password", hp("test") == hp("test") and len(hp("test")) == 64)
    ck("hash differs", hp("a") != hp("b"))
    # Owner login
    from config import config as cfg
    r = vl(str(cfg.telegram.owner_id), cfg.web.owner_web_pass)
    ck("owner login", r["ok"] and r["is_owner"])
    # Wrong owner password
    r = vl(str(cfg.telegram.owner_id), "wrong")
    ck("wrong owner pwd", not r["ok"])
    # Non-existent user
    r = vl("999999999999", "test")
    ck("non-existent user", not r["ok"])
    # Empty fields
    r = vl("", "")
    ck("empty fields", not r["ok"])
except Exception as e: ck("auth logic", False, str(e)[:80])

# [3] Flask test client (7)
print("\n[3] Flask client (7)")
from web.app import app as flask_app
client = flask_app.test_client()

# GET / redirects to /login
r = client.get("/", follow_redirects=False)
ck("GET / redirects", r.status_code in (301, 302), f"status={r.status_code}")

# GET /login returns 200
r = client.get("/login")
ck("GET /login", r.status_code == 200)
ck("login has HTML", b"SPIDER" in r.data or b"Login" in r.data)

# GET /app without login → redirect
r = client.get("/app", follow_redirects=False)
ck("GET /app without auth", r.status_code in (301, 302, 303))

# GET /api/web/me without login → 401
r = client.get("/api/web/me")
ck("me without auth", r.status_code == 401)

# GET /api/health works without login
r = client.get("/api/health")
ck("health public", r.status_code == 200)
data = r.get_json()
ck("health JSON", "status" in data and data["status"] == "ok")

# [4] Login flow (5)
print("\n[4] Login flow (5)")
# Bad login
r = client.post("/login", data={"user_id": "8813635835", "password": "wrong"}, follow_redirects=False)
ck("bad login → 200 (re-show)", r.status_code == 200)

# Good login (owner)
from config import config as cfg
r = client.post("/login", data={"user_id": str(cfg.telegram.owner_id), "password": cfg.web.owner_web_pass}, follow_redirects=False)
ck("good login → 302", r.status_code in (301, 302, 303), f"status={r.status_code}")

# Session established
r = client.get("/api/web/me")
ck("me after login", r.status_code == 200)
data = r.get_json()
ck("me has id", data.get("id") == str(cfg.telegram.owner_id))
ck("me is_owner", data.get("is_owner") == True)

# [5] Owner API (4)
print("\n[5] Owner API (4)")
r = client.get("/api/health/detail")
ck("health detail", r.status_code == 200)
data = r.get_json()
ck("health has bot", "bot" in data)
ck("health has users", "users" in data)
ck("health db ok", data.get("db") == True)

# [6] Templates (3)
print("\n[6] Templates (3)")
base = Path(__file__).parent.parent.parent
tpl = base / "web" / "templates"
ck("templates dir", tpl.exists())
ck("login.html exists", (tpl / "login.html").exists())
ck("preview.html exists", (tpl / "preview.html").exists())

# [7] Logout (2)
print("\n[7] Logout (2)")
r = client.get("/logout", follow_redirects=False)
ck("logout redirects", r.status_code in (301, 302, 303))
r = client.get("/api/web/me")
ck("me after logout 401", r.status_code == 401)

# [8] main.py (1)
print("\n[8] main.py (1)")
try:
    import main as m_main
    ck("do_run_web exists", hasattr(m_main, "do_run_web"))
except Exception as e: ck("main", False, str(e)[:60])

# Final
print("\n" + "=" * 55)
total = passed + failed
print(f"📊 النتيجة: ✅ {passed}/{total} · ❌ {failed}")
print("=" * 55)
if failed > 0:
    print(f"\n❌ {failed} فشل")
    sys.exit(1)
