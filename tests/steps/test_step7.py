"""Step 7 — Remaining Endpoints — 50+ tests"""
import sys, asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try: asyncio.get_running_loop()
except RuntimeError:
    try: asyncio.get_event_loop()
    except RuntimeError: asyncio.set_event_loop(asyncio.new_event_loop())

passed = failed = 0
def ck(name, cond, detail=""):
    global passed, failed
    if cond: passed += 1; print(f"  ✅ {name}" + (f" — {detail}" if detail else ""))
    else: failed += 1; print(f"  ❌ {name}" + (f" — {detail}" if detail else ""))

print("=" * 55)
print("🧪 اختبار الخطوة 7 — Remaining Endpoints")
print("=" * 55)

from database.migrations import apply_all
apply_all()

# Setup: Flask client with owner login
from web.app import create_app
from config import config as cfg
app = create_app()
c = app.test_client()
c.post("/login", data={"user_id": str(cfg.telegram.owner_id), "password": cfg.web.owner_web_pass})

def check_endpoint(name, method, path, expected_status=200, json_body=None):
    try:
        if method == "GET":
            r = c.get(path)
        else:
            r = c.post(path, json=json_body or {})
        if r.status_code != expected_status:
            ck(name, False, f"HTTP {r.status_code}")
            return None
        return r.get_json() if r.is_json else {}
    except Exception as e:
        ck(name, False, str(e)[:60])
        return None

# [1] Blueprints registered (5)
print("\n[1] Blueprints (5)")
try:
    from web.routes import scrape_more, sessions, store, economy, misc, proxies
    ck("scrape_more", hasattr(scrape_more, "bp"))
    ck("sessions", hasattr(sessions, "bp"))
    ck("store", hasattr(store, "bp"))
    ck("economy", hasattr(economy, "bp"))
    ck("misc + proxies", hasattr(misc, "bp") and hasattr(proxies, "bp"))
except Exception as e:
    ck("blueprints", False, str(e)[:60])

# [2] Scrape more (3)
print("\n[2] scrape_more (3)")
d = check_endpoint("groups endpoint exists", "GET", "/api/web/scrape/groups")
ck("groups returns dict", isinstance(d, dict) and ("groups" in d or "error" in d))
d = check_endpoint("vault list", "GET", "/api/web/vault/list")
ck("vault has total", isinstance(d, dict) and "total" in d)
d = check_endpoint("vault stats", "GET", "/api/web/vault/stats")
ck("vault stats keys", isinstance(d, dict) and "total" in d)

# [3] Sessions (2)
print("\n[3] sessions (2)")
d = check_endpoint("sessions list", "GET", "/api/web/sessions/list")
ck("sessions is list", isinstance(d, dict) and "sessions" in d)

# add without valid phone
r = c.post("/api/web/sessions/add", json={"phone": "123"})
ck("sessions/add invalid phone", r.status_code == 400)

# [4] Store (6)
print("\n[4] store (6)")
d = check_endpoint("themes list", "GET", "/api/web/store/themes")
ck("themes dict", isinstance(d, dict) and "themes" in d)
ck("6 themes", len(d["themes"]) == 6 if d else False)

# Give owner points
from database.queries import users
users.update_points(cfg.telegram.owner_id, 100000)

d = check_endpoint("buy vip", "POST", "/api/web/store/vip", json_body={"days": 1, "price": 500})
ck("vip bought", d and d.get("ok"))

d = check_endpoint("buy theme", "POST", "/api/web/store/theme", json_body={"theme": "light"})
ck("theme bought", d and d.get("ok"))

r = c.post("/api/web/store/theme", json={"theme": "nonexistent"})
ck("bad theme 400", r.status_code == 400)

# [5] Economy (8)
print("\n[5] economy (8)")
# Reset daily_tasks before testing (idempotent)
from database.connection import get_db as _gdb_eco
_gdb_eco().execute("DELETE FROM daily_tasks WHERE user_id=?", (str(cfg.telegram.owner_id),), commit=True)
d = check_endpoint("tasks list", "GET", "/api/web/tasks")
ck("tasks is list", d and "tasks" in d)
ck("5 tasks", len(d["tasks"]) == 5 if d else False)

d = check_endpoint("claim t4", "POST", "/api/web/tasks/claim", json_body={"task_id": "t4"})
ck("claim ok", d and d.get("ok"))

# Same claim again fails
r = c.post("/api/web/tasks/claim", json={"task_id": "t4"})
ck("double claim fails", r.status_code == 200 and r.get_json().get("ok") == False)

# Reset wheel spins before test
from database.connection import get_db as _gdb
_gdb().execute("UPDATE users SET wheel_spins_today=0, last_wheel_date=NULL WHERE id=?", (str(cfg.telegram.owner_id),), commit=True)

d = check_endpoint("wheel spin", "POST", "/api/web/wheel/spin")
ck("wheel has won", d and "won" in d)
ck("wheel has idx", d and "idx" in d)

d = check_endpoint("daily box", "POST", "/api/web/daily_box")
ck("box has reward or error", d and ("reward" in d or "error" in d))

d = check_endpoint("achievements", "GET", "/api/web/achievements")
ck("achievements list", d and "achievements" in d)

d = check_endpoint("leaderboard", "GET", "/api/web/leaderboard")
ck("leaderboard list", d and "leaders" in d)

# [6] Misc (7)
print("\n[6] misc (7)")
d = check_endpoint("weather", "GET", "/api/web/weather?city=Cairo")
ck("weather text", d and ("text" in d or "error" in d))

d = check_endpoint("referrals", "GET", "/api/web/referrals")
ck("referrals link", d and "link" in d)

d = check_endpoint("stats chart", "GET", "/api/web/stats/chart")
ck("chart labels+data", d and "labels" in d and "data" in d)

d = check_endpoint("settings all", "GET", "/api/settings/all")
ck("settings dict", d and "settings" in d)

d = check_endpoint("settings set", "POST", "/api/settings/set", json_body={"key": "test_v2", "value": "hello"})
ck("settings set ok", d and d.get("ok"))

d = check_endpoint("settings read back", "GET", "/api/settings/all")
ck("settings persisted", d and d["settings"].get("test_v2") == "hello")

# [7] Proxies (3)
print("\n[7] proxies (3)")
d = check_endpoint("proxies list", "GET", "/api/web/proxies/list")
ck("proxies list", d and "proxies" in d)

d = check_endpoint("proxies stats", "GET", "/api/web/proxies/stats")
ck("proxies stats", d and "total" in d)

# [8] All endpoints require auth (7)
print("\n[8] auth required (7)")
c2 = app.test_client()  # no login
protected = [
    ("GET", "/api/web/scrape/groups"),
    ("GET", "/api/web/vault/list"),
    ("GET", "/api/web/sessions/list"),
    ("POST", "/api/web/store/vip"),
    ("GET", "/api/web/tasks"),
    ("GET", "/api/web/leaderboard"),
    ("GET", "/api/web/referrals"),
]
for method, path in protected:
    r = c2.get(path) if method == "GET" else c2.post(path, json={})
    ck(f"{path} needs auth", r.status_code == 401)

# [9] preview.html endpoints coverage (10)
print("\n[9] preview.html coverage (10)")
paths = [
    "/api/web/me", "/api/web/scrape/groups", "/api/web/vault/list",
    "/api/web/sessions/list", "/api/web/proxies/list", "/api/web/tasks",
    "/api/web/leaderboard", "/api/web/achievements", "/api/web/stats/chart",
    "/api/web/referrals",
]
ok_count = 0
for p in paths:
    r = c.get(p)
    if r.status_code == 200: ok_count += 1
ck("10/10 endpoints working", ok_count == 10, f"{ok_count}/10")

# Final
print("\n" + "=" * 55)
total = passed + failed
print(f"📊 النتيجة: ✅ {passed}/{total} · ❌ {failed}")
print("=" * 55)
if failed > 0:
    print(f"\n❌ {failed} فشل")
    sys.exit(1)
