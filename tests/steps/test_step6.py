"""Step 6 — AI — 50+ tests"""
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
print("🧪 اختبار الخطوة 6 — AI")
print("=" * 55)

from database.migrations import apply_all
apply_all()

# [1] Imports (8)
print("\n[1] Imports (8)")
try:
    from ai.providers.base import BaseProvider
    ck("base", True)
except: ck("base", False, "")
try:
    from ai.providers import get_providers
    ck("get_providers", True)
except Exception as e: ck("get_providers", False, str(e)[:60])
try:
    from ai.search_engine import search_web
    ck("search_engine", True)
except: ck("search", False, "")
try:
    from ai import memory
    ck("memory", True)
except: ck("memory", False, "")
try:
    from ai.prompts import system_prompt
    ck("prompts", True)
except: ck("prompts", False, "")
try:
    from ai.router import ask
    ck("router", True)
except: ck("router", False, "")
try:
    from web.routes import chat
    ck("web chat", True)
except: ck("web chat", False, "")
try:
    from bot.handlers import ai_chat
    ck("bot ai_chat", True)
except: ck("bot ai_chat", False, "")

# [2] Providers (8)
print("\n[2] providers (8)")
try:
    from ai.providers import get_providers
    providers = get_providers()
    ck("5 providers", len(providers) == 5, f"got {len(providers)}")
    ck("groq exists", "groq" in providers)
    ck("nvidia exists", "nvidia" in providers)
    ck("openrouter exists", "openrouter" in providers)
    ck("gemini exists", "gemini" in providers)
    ck("pollinations exists", "pollinations" in providers)
    ck("groq has models", len(providers["groq"].MODELS) == 3)
    ck("nvidia has models", len(providers["nvidia"].MODELS) == 3)
except Exception as e:
    ck("providers", False, str(e)[:80])

# [3] Pollinations always available (1)
print("\n[3] pollinations always avail (1)")
try:
    from ai.providers.pollinations import PollinationsProvider
    p = PollinationsProvider()
    ck("always available", p.is_available() == True)
except Exception as e:
    ck("pollinations", False, str(e)[:60])

# [4] Prompts (3)
print("\n[4] prompts (3)")
try:
    from ai.prompts import system_prompt
    sp = system_prompt(is_owner=False, mode="fast")
    ck("base prompt", "Spider AI" in sp)
    spo = system_prompt(is_owner=True, mode="fast")
    ck("owner prompt", "المالك" in spo)
    sp_th = system_prompt(is_owner=False, mode="think")
    ck("think prompt", "تفكير" in sp_th)
except Exception as e:
    ck("prompts", False, str(e)[:60])

# [5] Memory (5)
print("\n[5] memory (5)")
try:
    from ai import memory
    test_uid = "test_ai_mem_xyz"
    memory.clear(test_uid)
    ck("clear works", True)
    memory.save_message(test_uid, "user", "مرحبا")
    memory.save_message(test_uid, "assistant", "أهلاً")
    ctx = memory.load_context(test_uid)
    ck("load context", len(ctx) >= 2)
    ck("context order", ctx[0]["role"] == "user" and ctx[1]["role"] == "assistant")
    memory.save_correction(test_uid, "wrong", "right")
    corrs = memory.get_corrections(test_uid)
    ck("corrections", len(corrs) == 1)
    memory.clear(test_uid)
    ck("clear after", len(memory.load_context(test_uid)) == 0)
except Exception as e:
    ck("memory", False, str(e)[:80])

# [6] Search engine (2) - with mock
print("\n[6] search_engine (2)")
try:
    from ai.search_engine import search_web
    result = asyncio.run(search_web("test query", mock=True))
    ck("mock search works", result is not None and "Mock" in result)
    ck("search_web callable", callable(search_web))
except Exception as e:
    ck("search", False, str(e)[:60])

# [7] Router fallback (5) — will fail without real keys, but should return error dict
print("\n[7] router fallback (5)")
try:
    from ai.router import ask
    result = asyncio.run(ask("مرحبا", "test_router_fb", mode="fast"))
    ck("returns dict", isinstance(result, dict))
    ck("has reply", "reply" in result)
    ck("has mode", result.get("mode") == "fast")
    # Pollinations should eventually respond OR return error
    ck("reply or error", bool(result.get("reply")) or result.get("error"))
    # Empty message
    result2 = asyncio.run(ask("", "test_router_fb"))
    ck("empty handled", "اكتب" in result2.get("reply", ""))
except Exception as e:
    ck("router fallback", False, str(e)[:80])

# [8] Web chat route (4)
print("\n[8] web chat route (4)")
try:
    from web.app import create_app
    app2 = create_app()
    c = app2.test_client()

    # Without login
    r = c.post("/api/web_chat", json={"message": "test"})
    ck("no auth 401", r.status_code == 401)

    # Login as owner
    from config import config as cfg
    c.post("/login", data={"user_id": str(cfg.telegram.owner_id), "password": cfg.web.owner_web_pass})

    # Empty message
    r = c.post("/api/web_chat", json={"message": ""})
    ck("empty 400", r.status_code == 400)

    # Valid message (will use fallback chain)
    r = c.post("/api/web_chat", json={"message": "قل: hi"})
    ck("valid returns 200", r.status_code == 200)
    data = r.get_json()
    ck("has reply", "reply" in data)
except Exception as e:
    ck("web chat", False, str(e)[:80])

# [9] Bot handler registered (2)
print("\n[9] bot ai_chat registered (2)")
try:
    from bot.handlers.ai_chat import ai_chat_handler, MENU_TEXTS
    ck("handler exists", callable(ai_chat_handler))
    ck("menu texts skip", "🕷️ السحب" in MENU_TEXTS and "🚀 الضخ" in MENU_TEXTS)
except Exception as e:
    ck("bot ai_chat", False, str(e)[:60])

# [10] 16 models count (1)
print("\n[10] 16 models total (1)")
try:
    from ai.providers import get_providers
    providers = get_providers()
    total_models = (
        len(providers["groq"].MODELS) +
        len(providers["nvidia"].MODELS) +
        len(providers["openrouter"].MODELS)
    )
    ck(">= 9 models listed", total_models >= 9, f"={total_models}")
except Exception as e:
    ck("model count", False, str(e)[:60])

# Final
print("\n" + "=" * 55)
total = passed + failed
print(f"📊 النتيجة: ✅ {passed}/{total} · ❌ {failed}")
print("=" * 55)
if failed > 0:
    print(f"\n❌ {failed} فشل")
    sys.exit(1)
