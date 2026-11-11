"""Spider V2 — Main Entry Point"""
import sys
import os
import signal
import asyncio
import argparse
import threading
import time
from pathlib import Path
from config import config, CONFIG_VERSION
from logger import get_logger, log_startup, log_shutdown

PID_FILE = config.paths.base_dir / "spider_v2.pid"
EXIT_OK = 0
EXIT_CONFIG = 1
EXIT_ALREADY = 3

def banner():
    print("\033[95m" + "=" * 55 + "\033[0m")
    print("\033[95m🕷️  SPIDER V2 — " + CONFIG_VERSION + "\033[0m")
    print("\033[95m" + "=" * 55 + "\033[0m")

def check_pid():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 0)
            return pid
        except (OSError, ValueError):
            PID_FILE.unlink(missing_ok=True)
    return None

def do_check():
    banner()
    print(f"\n📁 ENV: {config.paths.env_file}")
    print(f"🖥️  MODE: {config.env_mode}")
    print(f"\n🔑 Secrets (masked):")
    for k, v in config.mask_secrets().items():
        print(f"   {k:<15} → {v}")
    print(f"\n🏥 Health Check:")
    for k, v in config.health_check().items():
        print(f"   {k:<15} → {v}")
    errs = config.validate_all()
    if errs:
        print(f"\n❌ {len(errs)} errors:")
        for e in errs:
            print(f"   - {e['key']}: {e['reason']}")
        return EXIT_CONFIG
    print(f"\n✅ All checks passed!")
    return EXIT_OK

async def run_bot():
    from bot.client import start_bot, stop_bot
    ok = await start_bot()
    if not ok:
        return EXIT_CONFIG
    print(f"\n✅ Bot running. Ctrl+C to stop.\n")
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await stop_bot()
    return EXIT_OK

def do_run_bot():
    banner()
    log_startup()
    running = check_pid()
    if running:
        print(f"❌ Already running (PID: {running})")
        return EXIT_ALREADY
    if config.validate_all():
        print("❌ Config errors. Run --check")
        return EXIT_CONFIG
    config.ensure_directories()
    PID_FILE.write_text(str(os.getpid()))
    try:
        return asyncio.run(run_bot())
    finally:
        PID_FILE.unlink(missing_ok=True)
        log_shutdown()

def do_run_web(debug=False):
    banner()
    log_startup()
    log = get_logger("main")
    if config.validate_all():
        print("❌ Config errors. Run --check")
        return EXIT_CONFIG
    config.ensure_directories()

    from web.app import app
    port = config.web.web_port
    log.info(f"Web server starting on port {port}")
    print(f"\n🌐 Web: http://0.0.0.0:{port}")
    print(f"🔐 Login: http://127.0.0.1:{port}/login")
    print(f"🎨 App: http://127.0.0.1:{port}/app\n")
    try:
        app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        log.info("Web server stopped")
    finally:
        log_shutdown()
    return EXIT_OK

def do_run_ai_service():
    banner()
    log_startup()
    log = get_logger("main")
    print(f"🧠 AI Service: http://127.0.0.1:{config.web.ai_port}")
    print(f"🏥 Health: http://127.0.0.1:{config.web.ai_port}/health\n")
    try:
        from services.ai_service import run_ai_service
        run_ai_service()
    except KeyboardInterrupt:
        log.info("AI service stopped")
    finally:
        log_shutdown()
    return EXIT_OK

def do_run_all(debug=False):
    """يشغل AI service في thread + Web في main thread"""
    banner()
    log_startup()
    log = get_logger("main")
    if config.validate_all():
        print("❌ Config errors. Run --check")
        return EXIT_CONFIG
    config.ensure_directories()

    # Start AI service in background thread
    def _ai_thread():
        try:
            from services.ai_service import app as ai_app
            ai_app.run(host="127.0.0.1", port=config.web.ai_port, threaded=True, use_reloader=False)
        except Exception as e:
            log.error(f"AI service failed: {e}")

    ai_thread = threading.Thread(target=_ai_thread, daemon=True)
    ai_thread.start()
    time.sleep(2)  # Wait for AI service to start

    # Verify AI service
    try:
        import httpx
        r = httpx.get(f"http://127.0.0.1:{config.web.ai_port}/health", timeout=3)
        if r.status_code == 200:
            print(f"✅ AI Service running on port {config.web.ai_port}")
        else:
            print(f"⚠️  AI Service responded with {r.status_code}")
    except Exception as e:
        print(f"⚠️  AI Service check failed: {str(e)[:60]}")

    # Start Web in main thread
    print(f"\n🌐 Web: http://0.0.0.0:{config.web.web_port}")
    print(f"🔐 Login: http://127.0.0.1:{config.web.web_port}/login")
    print(f"🎨 App: http://127.0.0.1:{config.web.web_port}/app\n")
    try:
        from web.app import app
        app.run(host="0.0.0.0", port=config.web.web_port, debug=debug, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        log.info("All services stopped")
    finally:
        log_shutdown()
    return EXIT_OK

def main():
    parser = argparse.ArgumentParser(description="Spider V2")
    parser.add_argument("--check", action="store_true", help="فحص الإعدادات")
    parser.add_argument("--version", action="store_true", help="الإصدار")
    parser.add_argument("--debug", action="store_true", help="وضع التطوير")
    parser.add_argument("--test", type=str, help="تشغيل اختبار")
    parser.add_argument("--bot", action="store_true", help="البوت فقط")
    parser.add_argument("--web", action="store_true", help="الموقع فقط")
    parser.add_argument("--ai-service", action="store_true", help="AI service فقط")
    parser.add_argument("--all", action="store_true", help="كل الخدمات")
    args = parser.parse_args()

    if args.version:
        print(f"Spider V2 v{CONFIG_VERSION}")
        return EXIT_OK
    if args.debug:
        os.environ["ENV_MODE"] = "dev"
    if args.test:
        import subprocess
        return subprocess.run([sys.executable, "tests/runner.py", args.test]).returncode
    if args.check:
        return do_check()
    if args.bot:
        return do_run_bot()
    if args.web:
        return do_run_web(debug=args.debug)
    if args.ai_service:
        return do_run_ai_service()
    if args.all:
        return do_run_all(debug=args.debug)

    print("⚠️  حدد وضع: --bot, --web, --ai-service, --all, --check")
    return EXIT_CONFIG

if __name__ == "__main__":
    sys.exit(main())
