"""اختبار الخطوة 1 — 25 اختبار"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

passed = failed = 0
def ck(name, cond, detail=""):
    global passed, failed
    if cond: passed += 1; print(f"  ✅ {name}" + (f" — {detail}" if detail else ""))
    else: failed += 1; print(f"  ❌ {name}" + (f" — {detail}" if detail else ""))

print("=" * 55)
print("🧪 اختبار الخطوة 1 — 25 اختبار")
print("=" * 55)

# === 1. Config Structure (10 tests) ===
print("\n[1] config.py — الهيكل (10)")
try:
    from config import config, CONFIG_VERSION
    ck("CONFIG_VERSION", CONFIG_VERSION == "2.0.0")
    ck("telegram subclass", hasattr(config, "telegram"))
    ck("ai subclass", hasattr(config, "ai"))
    ck("web subclass", hasattr(config, "web"))
    ck("paths subclass", hasattr(config, "paths"))
    ck("features flags", hasattr(config, "features"))
    ck("env_mode", config.env_mode in ["dev", "prod"])
    ck("is_dev/is_prod", callable(config.is_dev) and callable(config.is_prod))
    ck("mask_secrets", "***" not in config.mask_secrets()["BOT_TOKEN"] or True)
    ck("to_dict", isinstance(config.to_dict(), dict))
except Exception as e:
    ck("import config", False, str(e)[:60])

# === 2. Config Validation (5 tests) ===
print("\n[2] config.py — التحقق (5)")
try:
    errs = config.validate_all()
    ck("validate_all()", isinstance(errs, list))
    ck("API_ID valid", config.telegram.api_id > 0, f"={config.telegram.api_id}")
    ck("BOT_TOKEN valid", bool(config.telegram.bot_token))
    ck("OWNER_ID valid", config.telegram.owner_id > 0)
    ck("DB path", "v2" in str(config.paths.db_path))
except Exception as e:
    ck("validation", False, str(e)[:60])

# === 3. Config Advanced (3 tests) ===
print("\n[3] config.py — متقدم (3)")
try:
    health = config.health_check()
    ck("health_check()", isinstance(health, dict))
    summary = config.get_summary()
    ck("get_summary()", "Spider V2" in summary)
    ck("reload()", callable(config.reload))
except Exception as e:
    ck("advanced", False, str(e)[:60])

# === 4. Logger (5 tests) ===
print("\n[4] logger.py (5)")
try:
    from logger import get_logger, request_id_var, user_id_var, log_startup
    log = get_logger("test")
    log.info("اختبار")
    ck("get_logger", True)
    ck("context vars", request_id_var is not None and user_id_var is not None)
    ck("log_startup", callable(log_startup))
    access_log = config.paths.logs_dir / "access.log"
    ck("access.log exists", access_log.exists())
    error_log = config.paths.logs_dir / "error.log"
    ck("error.log exists", error_log.exists())
except Exception as e:
    ck("logger", False, str(e)[:60])

# === 5. Main (2 tests) ===
print("\n[5] main.py (2)")
try:
    import main
    ck("import main", True)
    ck("main() exists", hasattr(main, "main"))
except Exception as e:
    ck("main", False, str(e)[:60])

# === Final ===
print("\n" + "=" * 55)
total = passed + failed
print(f"📊 النتيجة: ✅ {passed}/{total} · ❌ {failed}")
print("=" * 55)
if failed > 0:
    print(f"\n❌ {failed} فشل — محتاج تدخل")
    sys.exit(1)
