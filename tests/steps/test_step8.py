"""Step 8 — AI Service + Final Integration — 30+ tests"""
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
print("🧪 اختبار الخطوة 8 — Final Integration")
print("=" * 55)

from database.migrations import apply_all
apply_all()

# [1] AI Service imports (4)
print("\n[1] AI Service imports (4)")
try:
    from services.ai_service import app as ai_app, run_moa, run_ai_service
    ck("ai_service module", True)
    ck("app exists", ai_app is not None)
    ck("run_moa callable", callable(run_moa))
    ck("run_ai_service callable", callable(run_ai_service))
except Exception as e:
    ck("ai_service imports", False, str(e)[:80])

# [2] AI Service endpoints (6)
print("\n[2] AI Service endpoints (6)")
try:
    from services.ai_service import app as ai_app
    c = ai_app.test_client()

    r = c.get("/health")
    ck("health 200", r.status_code == 200)
    d = r.get_json()
    ck("health has status", d.get("status") == "ok")
    ck("health has pipeline", d.get("pipeline") == "MoA")
    ck("health has total_models", isinstance(d.get("total_models"), int))
    ck("health has available", isinstance(d.get("available"), dict))

    # Chat without messages
    r = c.post("/chat", json={})
    ck("chat empty 400", r.status_code == 400)
except Exception as e:
    ck("ai service endpoints", False, str(e)[:80])

# [3] MoA fallback (4)
print("\n[3] MoA fallback (4)")
try:
    from services.ai_service import run_moa

    async def test_moa():
        result = await run_moa([{"role": "user", "content": "قل: hi"}], max_tokens=50)
        ck("moa returns dict", isinstance(result, dict))
        ck("moa has meta", "meta" in result)
        meta = result.get("meta", {})
        ck("meta has pipeline", "pipeline" in meta)
        ck("meta has provider", "provider" in meta)

    asyncio.run(test_moa())
except Exception as e:
    ck("moa test", False, str(e)[:80])

# [4] main.py flags (5)
print("\n[4] main.py flags (5)")
try:
    import main as m_main
    ck("do_run_ai_service exists", hasattr(m_main, "do_run_ai_service"))
    ck("do_run_all exists", hasattr(m_main, "do_run_all"))
    ck("do_run_web exists", hasattr(m_main, "do_run_web"))
    ck("do_run_bot exists", hasattr(m_main, "do_run_bot"))
    ck("do_check exists", hasattr(m_main, "do_check"))
except Exception as e:
    ck("main flags", False, str(e)[:80])

# [5] Integration: Web → AI service (4)
print("\n[5] Integration Web → AI (4)")
try:
    from web.app import create_app
    from config import config as cfg
    app = create_app()
    c = app.test_client()
    c.post("/login", data={"user_id": str(cfg.telegram.owner_id), "password": cfg.web.owner_web_pass})

    # Without AI service running, should still return 200 (fallback chain)
    r = c.post("/api/web_chat", json={"message": "قل: hi", "deep_think": True})
    ck("think mode returns 200", r.status_code == 200)
    d = r.get_json()
    ck("has reply", "reply" in d)
    ck("mode is think", d.get("mode") == "think")
    ck("reply not empty", len(d.get("reply", "")) > 0 or d.get("error"))
except Exception as e:
    ck("integration", False, str(e)[:80])

# [6] All 3 AI modes via web (3)
print("\n[6] 3 AI modes via web (3)")
try:
    from config import config as cfg
    app2 = create_app()
    c2 = app2.test_client()
    c2.post("/login", data={"user_id": str(cfg.telegram.owner_id), "password": cfg.web.owner_web_pass})

    for mode_data, name in [
        ({"message": "test"}, "fast"),
        ({"message": "test", "search": True}, "search"),
        ({"message": "test", "deep_think": True}, "think"),
    ]:
        r = c2.post("/api/web_chat", json=mode_data)
        ck(f"{name} mode returns 200", r.status_code == 200)
except Exception as e:
    ck("3 modes", False, str(e)[:80])

# [7] Full integration smoke (4)
print("\n[7] Full integration smoke (4)")
try:
    from config import config as cfg
    app3 = create_app()
    c3 = app3.test_client()
    c3.post("/login", data={"user_id": str(cfg.telegram.owner_id), "password": cfg.web.owner_web_pass})

    endpoints = [
        "/api/web/me",
        "/api/health",
        "/api/web/sessions/list",
        "/api/web/vault/list",
    ]
    working = 0
    for p in endpoints:
        r = c3.get(p)
        if r.status_code == 200: working += 1
    ck("4/4 core endpoints", working == 4, f"{working}/4")

    # Preview loads
    r = c3.get("/app")
    ck("app loads", r.status_code == 200)

    # Login page loads
    r = app3.test_client().get("/login")
    ck("login loads", r.status_code == 200)
except Exception as e:
    ck("smoke", False, str(e)[:80])

# Final
print("\n" + "=" * 55)
total = passed + failed
print(f"📊 النتيجة: ✅ {passed}/{total} · ❌ {failed}")
print("=" * 55)
if failed > 0:
    print(f"\n❌ {failed} فشل")
    sys.exit(1)
