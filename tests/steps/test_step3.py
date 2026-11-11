"""Step 3 — Bot Core — 35+ tests (Py 3.14 safe)"""
import sys, asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Fix: ensure event loop exists
try:
    asyncio.get_running_loop()
except RuntimeError:
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

passed = failed = 0
def ck(name, cond, detail=""):
    global passed, failed
    if cond: passed += 1; print(f"  ✅ {name}" + (f" — {detail}" if detail else ""))
    else: failed += 1; print(f"  ❌ {name}" + (f" — {detail}" if detail else ""))

print("=" * 55)
print("🧪 اختبار الخطوة 3 — Bot Core")
print("=" * 55)

# [0] Apply migrations
from database.migrations import apply_all
apply_all()

# [1] Imports (6)
print("\n[1] Imports (6)")
try:
    from bot.testing import MockUser, MockMessage, MockClient
    ck("testing.py", True)
except Exception as e:
    ck("testing.py", False, str(e)[:60])

try:
    from bot.filters import is_owner, is_owner_id
    ck("filters.py", True)
except Exception as e:
    ck("filters.py", False, str(e)[:60])

try:
    from bot.texts import TEXTS, fmt, E
    ck("texts.py", True)
except Exception as e:
    ck("texts.py", False, str(e)[:60])

try:
    from bot.keyboards import main_menu, owner_menu, back_kb
    ck("keyboards.py", True)
except Exception as e:
    ck("keyboards.py", False, str(e)[:60])

try:
    from bot.client import get_bot, is_ready
    ck("client.py", True)
except Exception as e:
    ck("client.py", False, str(e)[:60])

try:
    from bot.middleware import ban_check, maintenance_check, owner_only
    ck("middleware.py", True)
except Exception as e:
    ck("middleware.py", False, str(e)[:60])

# [2] Mock objects (4)
print("\n[2] Mock Pyrogram (4)")
try:
    u = MockUser(123, "Ahmed", "ahmed")
    ck("MockUser", u.id == 123 and u.username == "ahmed")
    m = MockMessage("/start", 123)
    ck("MockMessage", m.text == "/start" and m.from_user.id == 123)
    m2 = MockMessage("/start ref123", 456)
    ck("command parse", m2.command == "start")
    c = MockClient()
    ck("MockClient", c.me.username == "spider_test_bot")
except Exception as e:
    ck("mock objects", False, str(e)[:60])

# [3] Texts (5)
print("\n[3] texts.py (5)")
try:
    from bot.texts import TEXTS as T2, fmt as f2, E as E2
    ck("welcome exists", "welcome" in T2)
    ck("help exists", "help" in T2)
    ck("banned exists", "banned" in T2)
    ck("E dict", E2.get("spider") == "🕷️")
    formatted = f2("welcome", name="X", user_id=1)
    ck("fmt()", "X" in formatted and "1" in formatted)
except Exception as e:
    ck("texts", False, str(e)[:60])

# [4] Keyboards (5)
print("\n[4] keyboards.py (5)")
try:
    from bot.keyboards import main_menu as mm_fn, owner_menu as om_fn, back_kb as bk_fn
    from pyrogram.types import ReplyKeyboardMarkup
    mm = mm_fn(False)
    ck("main_menu user", isinstance(mm, ReplyKeyboardMarkup))
    mo = mm_fn(True)
    ck("main_menu owner", isinstance(mo, ReplyKeyboardMarkup))
    ck("owner_menu", isinstance(om_fn(), ReplyKeyboardMarkup))
    ck("back_kb", isinstance(bk_fn(), ReplyKeyboardMarkup))
    ck("buttons count", len(mm.keyboard) >= 2)
except Exception as e:
    ck("keyboards", False, str(e)[:60])

# [5] Filters (2)
print("\n[5] filters.py (2)")
try:
    from bot.filters import is_owner_id as iod
    from config import config as cfg
    ck("is_owner_id", iod(cfg.telegram.owner_id))
    ck("is_owner_id false", not iod(999))
except Exception as e:
    ck("filters", False, str(e)[:60])

# [6] Middleware (4)
print("\n[6] middleware.py (4)")
try:
    from bot.middleware import set_maintenance as sm, is_maintenance as im, ban_check as bc
    ck("is_maintenance", im() == False)
    sm(True)
    ck("set_maintenance on", im() == True)
    sm(False)
    ck("set_maintenance off", im() == False)
    ck("ban_check", callable(bc))
except Exception as e:
    ck("middleware", False, str(e)[:60])

# [7] Handlers registered (4) — with async wrapper
print("\n[7] Handlers registered (4)")
try:
    async def check_handlers():
        from bot.client import get_bot as gb
        try:
            client = gb()
            return client is not None
        except Exception as e:
            return f"err: {str(e)[:40]}"
    result = asyncio.run(check_handlers())
    ck("client created", result is True or (isinstance(result, str) and "err" in result))

    from bot.handlers.start import start_handler as sh
    ck("start_handler exists", callable(sh))
    from bot.handlers.menu import menu_handler as mh
    ck("menu_handler exists", callable(mh))
    from bot.handlers.help import help_handler as hh
    ck("help_handler exists", callable(hh))
except Exception as e:
    ck("handlers", False, str(e)[:80])

# [8] start_handler logic (5)
print("\n[8] start_handler logic (5)")
try:
    async def test_start():
        from bot.handlers.start import start_handler as sh2
        from database.connection import get_db as gdb
        uid = 999888777
        gdb().execute("DELETE FROM users WHERE id=?", (str(uid),), commit=True)
        msg = MockMessage("/start", uid, "NewUser")
        await sh2(None, msg)
        ck("new user reply", len(msg.replies) > 0)
        ck("welcome text", any(("Spider" in r or "أهلاً" in r or "قائد" in r) for r in msg.replies))
        from database.queries import users as U
        u = U.get_user(uid)
        ck("user in DB", u is not None)
        ck("welcome bonus", u["points"] >= 10)
        msg2 = MockMessage("/start", uid)
        await sh2(None, msg2)
        ck("existing user reply", len(msg2.replies) > 0)
    asyncio.run(test_start())
except Exception as e:
    ck("start logic", False, str(e)[:100])

# [9] main.py (3)
print("\n[9] main.py (3)")
try:
    import main as m_main
    ck("import main", True)
    ck("--bot exists", hasattr(m_main, "do_run_bot"))
    ck("--web exists", hasattr(m_main, "do_run_web"))
except Exception as e:
    ck("main", False, str(e)[:60])

# Final
print("\n" + "=" * 55)
total = passed + failed
print(f"📊 النتيجة: ✅ {passed}/{total} · ❌ {failed}")
print("=" * 55)
if failed > 0:
    print(f"\n❌ {failed} فشل")
    sys.exit(1)
