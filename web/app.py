"""Flask App Factory"""
import time
from flask import Flask, jsonify, request, session
from config import config
from logger import get_logger


# ═══ Pyrogram Preload (Python 3.14 fix) ═══
import asyncio as _asyncio
try:
    _asyncio.get_running_loop()
except RuntimeError:
    try:
        _asyncio.get_event_loop()
    except RuntimeError:
        _asyncio.set_event_loop(_asyncio.new_event_loop())

try:
    from pyrogram import Client as _PC, enums as _PE
    print("[Preload] ✅ Pyrogram loaded")
except Exception as _e:
    print(f"[Preload] ⚠️ Pyrogram not loaded: {_e}")

# ═══ End Preload ═══

log = get_logger("web")


import asyncio as _asyncio
import threading as _thr
import time as _time
import concurrent.futures as _cf

# ═══ Pyrogram Worker Loop ═══
_pyro_loop = None
_pyro_loop_lock = _thr.Lock()

def _ensure_loop():
    global _pyro_loop
    if _pyro_loop is not None and not _pyro_loop.is_closed():
        return _pyro_loop
    with _pyro_loop_lock:
        if _pyro_loop is not None and not _pyro_loop.is_closed():
            return _pyro_loop
        loop = _asyncio.new_event_loop()

        def _run():
            _asyncio.set_event_loop(loop)
            print("[PyroWorker] Loop started")
            loop.run_forever()

        _thr.Thread(target=_run, daemon=True, name="PyroWorker").start()
        _pyro_loop = loop
        _time.sleep(0.5)
        return loop

def get_pyro_loop():
    return _ensure_loop()

def run_pyro(coro, timeout=60):
    """Run async coroutine on persistent Pyrogram loop"""
    try:
        loop = _ensure_loop()
        future = _asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result(timeout=timeout)
    except _cf.TimeoutError:
        return {"error": f"timeout ({timeout}s)"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:100]}"}
# ═══ End Pyrogram Worker ═══

def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.secret_key = config.web.flask_secret
    app.config["PERMANENT_SESSION_LIFETIME"] = 30 * 24 * 3600
    app.config["JSON_AS_ASCII"] = False

    # Request logging
    @app.before_request
    def before():
        request._start_time = time.time()

    @app.after_request
    def after(response):
        elapsed = (time.time() - getattr(request, "_start_time", time.time())) * 1000
        if not request.path.startswith("/static"):
            log.debug(f"{request.method} {request.path} → {response.status_code} ({elapsed:.0f}ms)")
        if request.path.startswith("/static/"):
            response.headers["Cache-Control"] = "public, max-age=3600"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not Found", "path": request.path}), 404
        return "404 — Not Found", 404

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden"}), 403

    @app.errorhandler(500)
    def server_error(e):
        log.error(f"500 on {request.path}")
        return jsonify({"error": "Internal Server Error"}), 500

    # Favicon
    @app.route("/favicon.ico")
    def favicon():
        from flask import Response
        return Response(status=204)

    # Register routes
    from web.routes import register_routes
    register_routes(app)

    log.info(f"Flask app ready (secret: {'set' if config.web.flask_secret else 'MISSING'})")
    return app

app = create_app()


# ═══ Scheduler Worker ═══
import time as _time
from datetime import datetime

def _scheduler_worker():
    _time.sleep(10) # انتظار بدء السيرفر
    while True:
        try:
            db = get_db()
            now = datetime.now().strftime("%H:%M")
            today = datetime.now().strftime("%Y-%m-%d")
            
            # البحث عن المهام المستحقة
            tasks = db.fetchall("SELECT * FROM scheduled_tasks WHERE status='PENDING' AND run_at <= ?", (now,))
            
            for t in tasks:
                # تحديث الحالة لمنع التكرار
                db.execute("UPDATE scheduled_tasks SET status='RUNNING' WHERE id=?", (t['id'],), commit=True)
                
                # تنفيذ المهمة
                if t['type'] == 'scrape':
                    import requests
                    headers = {'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true'}
                    payload = {'chat_id': t['chat_id'], 'mode': t['mode'], 'filter': t.get('filter_type', 'all')}
                    # بنبعت طلب داخلي للسيرفر نفسه عشان نستخدم نفس اللوجيك بتاعنا
                    try: requests.post('http://127.0.0.1:8090/api/web/scrape/start', json=payload, headers=headers)
                    except: pass
                elif t['type'] == 'pump':
                    import requests
                    headers = {'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true'}
                    payload = {'chat_id': t['chat_id'], 'mode': t['mode']}
                    try: requests.post('http://127.0.0.1:8090/api/web/pump/start', json=payload, headers=headers)
                    except: pass
                    
        except Exception as e:
            pass
        _time.sleep(60) # فحص كل دقيقة

# تشغيل العداد في الخلفية
import threading
threading.Thread(target=_scheduler_worker, daemon=True).start()
