"""Step 5 — Scrape & Pump — 45+ tests"""
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
print("🧪 اختبار الخطوة 5 — Scrape & Pump")
print("=" * 55)

from database.migrations import apply_all
apply_all()

# [1] Imports (10)
print("\n[1] Imports (10)")
try:
    from scraper.session_manager import SessionPool
    ck("SessionPool", True)
except Exception as e: ck("SessionPool", False, str(e)[:60])

try:
    from scraper.validators import should_scrape, make_member_tuple
    ck("validators", True)
except Exception as e: ck("validators", False, str(e)[:60])

try:
    from scraper.progress import create, update, get, finish
    ck("progress", True)
except Exception as e: ck("progress", False, str(e)[:60])

try:
    from scraper.proxy_manager import fetch_free_proxies_sync, stats
    ck("proxy_manager", True)
except Exception as e: ck("proxy_manager", False, str(e)[:60])

try:
    from scraper.engine import run_scrape
    ck("engine", True)
except Exception as e: ck("engine", False, str(e)[:60])

try:
    from scraper.pump_engine import run_pump
    ck("pump_engine", True)
except Exception as e: ck("pump_engine", False, str(e)[:60])

try:
    from web.routes import scrape, pump
    ck("web routes", True)
except Exception as e: ck("web routes", False, str(e)[:60])

try:
    from tests.mock_tg_api import MockTGClient
    ck("MockTGClient", True)
except Exception as e: ck("MockTGClient", False, str(e)[:60])

try:
    from bot.handlers import scrape as hs, pump as hp
    ck("bot handlers", True)
except Exception as e: ck("bot handlers", False, str(e)[:60])

try:
    ck("blueprints", hasattr(scrape, "bp") and hasattr(pump, "bp"))
except Exception as e: ck("blueprints", False, str(e)[:60])

# [2] Validators (6)
print("\n[2] validators (6)")
try:
    from scraper.validators import should_scrape
    from bot.testing import MockUser
    u_ok = MockUser(1, "Ok", "ok")
    u_ok.is_bot = False
    u_no_uname = MockUser(2, "NoU", None)
    u_no_uname.is_bot = False
    u_bot = MockUser(3, "Bot", "bot")
    u_bot.is_bot = True

    r = should_scrape(u_ok, {"usernames_only": True})
    ck("ok user", r["ok"])
    r = should_scrape(u_ok, {"usernames_only": False})
    ck("ok user no filter", r["ok"])
    r = should_scrape(u_no_uname, {"usernames_only": True})
    ck("no username filtered", not r["ok"] and r["reason"] == "no_username")
    r = should_scrape(u_bot, {"usernames_only": False})
    ck("bot filtered", not r["ok"] and r["reason"] == "bot")
    r = should_scrape(None)
    ck("none filtered", not r["ok"])
    from scraper.validators import make_member_tuple
    tup = make_member_tuple(u_ok, "group123")
    ck("tuple format", len(tup) == 5 and tup[0] == "@ok")
except Exception as e:
    ck("validators tests", False, str(e)[:80])

# [3] Progress (5)
print("\n[3] progress (5)")
try:
    from scraper import progress as P
    tid = P.create("scrape", "test_owner_prog", "-100123")
    ck("create", tid is not None and len(tid) == 12)
    P.increment(tid, "scraped", 5)
    t = P.get(tid)
    ck("increment", t["scraped"] == 5)
    P.update(tid, status="running")
    t = P.get(tid)
    ck("update", t["status"] == "running")
    P.finish(tid, "completed")
    t = P.get(tid)
    ck("finish", t["status"] == "completed")
    # User active tasks
    t2 = P.create("scrape", "test_owner_prog2", "-100124")
    act = P.user_active_tasks("test_owner_prog2")
    ck("active tasks", t2 in act)
    P.finish(t2)
except Exception as e:
    ck("progress tests", False, str(e)[:80])

# [4] Session Manager (4)
print("\n[4] session_manager (4)")
try:
    from scraper.session_manager import SessionPool, SessionInfo
    pool = SessionPool("test_owner_sm", is_owner=False)
    s = pool.load()
    ck("load empty", isinstance(s, list))
    info = SessionInfo("test_sess", "test_owner", 5, "2026-01-01")
    info.successes = 8
    info.failures = 2
    ck("score calculation", info.score == 80)
    ck("is_alive", info.is_alive == True)
    # track result
    pool.track_result("test_sess_xyz", True)
    info2 = pool._stats.get("test_sess_xyz")
    ck("track result", info2 is not None and info2.successes == 1)
except Exception as e:
    ck("session manager", False, str(e)[:80])

# [5] Mock TG Client (4)
print("\n[5] MockTGClient (4)")
try:
    from tests.mock_tg_api import MockTGClient
    async def test_mock():
        c = MockTGClient(members_count=10, history_count=5)
        members = []
        async for m in c.get_chat_members(-100123):
            members.append(m)
        ck("members count", len(members) == 10)
        hist = []
        async for msg in c.get_chat_history(-100123):
            hist.append(msg)
        ck("history count", len(hist) == 5)
        await c.add_chat_members(-100123, 999)
        ck("add members", 999 in c.added)
    asyncio.run(test_mock())
    ck("mock ready", True)
except Exception as e:
    ck("mock client", False, str(e)[:80])

# [6] Engine (with Mock) — 6 tests
print("\n[6] engine.run_scrape with Mock (6)")
try:
    from scraper.engine import run_scrape
    from tests.mock_tg_api import MockTGClient
    from scraper import progress as P2
    from database.connection import get_db

    # Clean test data
    get_db().execute("DELETE FROM members WHERE owner_user_id=?", ("test_engine_owner",), commit=True)

    async def test_engine():
        client = MockTGClient(members_count=20, history_count=10)
        tid = P2.create("scrape", "test_engine_owner", "-100999")
        stats = await run_scrape(client, -100999, "test_engine_owner", tid,
                                 filters={"usernames_only": True})
        ck("engine returns stats", "scraped" in stats)
        ck("scraped > 0", stats["scraped"] > 0, f"={stats['scraped']}")
        ck("scanned > 0", stats["scanned"] > 0, f"={stats['scanned']}")
        ck("failed > 0 (filtered)", stats["failed"] > 0, f"={stats['failed']}")
        ck("filtered bots/no_username", stats["failed"] >= stats["scraped"] // 2)
        # Members saved
        cnt = get_db().fetchone("SELECT COUNT(*) as c FROM members WHERE owner_user_id=?", ("test_engine_owner",))["c"]
        ck("members saved", cnt > 0, f"={cnt}")

    asyncio.run(test_engine())
except Exception as e:
    ck("engine test", False, str(e)[:100])

# [7] Pump Engine (3)
print("\n[7] pump engine (3)")
try:
    from scraper.pump_engine import run_pump
    from tests.mock_tg_api import MockTGClient
    from scraper import progress as P3
    from database.connection import get_db

    # Seed members
    get_db().execute("DELETE FROM members WHERE owner_user_id=?", ("test_pump_owner",), commit=True)
    for i in range(5):
        get_db().execute(
            "INSERT INTO members (id, username, user_id, scraped_from, scraped_at, owner_user_id) VALUES (?, ?, ?, ?, datetime('now'), ?)",
            (f"@pump{i}", f"pump{i}", str(10000+i), "test", "test_pump_owner"),
            commit=True
        )

    async def test_pump():
        client = MockTGClient()
        tid = P3.create("pump", "test_pump_owner", "-100888")
        stats = await run_pump(client, -100888, "test_pump_owner", tid, mode="turbo", max_pumps=3)
        ck("pump stats", "success" in stats)
        ck("pump success > 0", stats["success"] > 0, f"={stats['success']}")
        ck("added tracked", len(client.added) > 0)

    asyncio.run(test_pump())
except Exception as e:
    ck("pump test", False, str(e)[:100])

# [8] Web Routes (3)
print("\n[8] web routes (3)")
try:
    from web.app import create_app
    app2 = create_app()
    client_w = app2.test_client()

    # without login → 401
    r = client_w.post("/api/web/scrape/start", json={"chat_id": -100123})
    ck("start without auth", r.status_code == 401)

    r = client_w.get("/api/web/scrape/status/abc")
    ck("status without auth", r.status_code == 401)

    # login as owner
    from config import config as cfg
    client_w.post("/login", data={"user_id": str(cfg.telegram.owner_id), "password": cfg.web.owner_web_pass})

    r = client_w.post("/api/web/scrape/start", json={})
    ck("start no chat_id", r.status_code == 400)
except Exception as e:
    ck("web routes", False, str(e)[:80])

# [9] Proxy manager (2)
print("\n[9] proxy_manager (2)")
try:
    from scraper.proxy_manager import stats as pstats, get_random_valid_proxy
    s = pstats()
    ck("stats keys", "total" in s and "valid" in s)
    p = get_random_valid_proxy()
    ck("get random", p is None or isinstance(p, str))
except Exception as e:
    ck("proxy manager", False, str(e)[:60])

# Final
print("\n" + "=" * 55)
total = passed + failed
print(f"📊 النتيجة: ✅ {passed}/{total} · ❌ {failed}")
print("=" * 55)
if failed > 0:
    print(f"\n❌ {failed} فشل")
    sys.exit(1)
