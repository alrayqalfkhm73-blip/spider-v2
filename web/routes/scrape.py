"""Scrape API — Clean Version with XP & Achievements"""
from flask import Blueprint, request, jsonify, session
from web.deps import require_login, get_uid
from database.queries import sessions as sess_q
from database.connection import get_db
from scraper import progress
from scraper.engine import run_scrape
from logger import get_logger

bp = Blueprint("scrape", __name__)
log = get_logger("web.scrape")
db = get_db()

@bp.route("/api/web/scrape/start", methods=["POST"])
@require_login
def scrape_start():
    uid = get_uid()
    data = request.json or {}
    target = data.get("chat_id")
    filter_type = data.get("filter", "all")

    if not target:
        return jsonify({"error": "chat_id مطلوب"}), 400

    active = progress.user_active_tasks(uid)
    if active:
        return jsonify({"error": f"فيه عملية شغالة ({active[0]})"}), 429

    filters = {}
    if filter_type == "usernames_only": filters["usernames_only"] = True
    elif filter_type == "with_photo": filters["with_photo"] = True

    task_id = progress.create("scrape", uid, str(target))

    async def _do():
        from pyrogram import Client
        from config import config
        import asyncio
        
        try:
            all_sess = sess_q.get_all(uid)
            actives = [s for s in all_sess if s.get("status") == "ACTIVE"]
            pool_sessions = actives[0] if actives else (all_sess[0] if all_sess else None)
                
            if not pool_sessions:
                progress.finish(task_id, "failed")
                progress.update(task_id, reason="مفيش جلسة مربوطة")
                return

            sess_name = str(pool_sessions["session_name"]).replace(".session", "")
            sess_path = str(config.paths.sessions_dir / sess_name)
            
            cli = None
            try:
                cli = Client(
                    sess_path,
                    api_id=config.telegram.api_id,
                    api_hash=config.telegram.api_hash,
                    no_updates=True,
                    device_model="Samsung SM-S918B"
                )
                await cli.connect()
                
                try:
                    async for _d in cli.get_dialogs(limit=200):
                        pass
                except Exception:
                    pass
                
                stats = await run_scrape(cli, target, uid, task_id, filters)
                
                try: sess_q.increment_scrape(sess_name)
                except: pass
                
                # ═══ إضافة الخبرة (XP) ═══
                if stats.get("scraped", 0) > 0:
                    xp_amount = stats["scraped"] * 2
                    from database.queries import users as users_q
                    lvl_res = users_q.add_xp(uid, xp_amount)
                    if lvl_res.get("level_up"):
                        try:
                            from web.routes.telegram_webhook import notify_user
                            notify_user(uid, f"🎉 <b>مبروك!</b>\\nلقد وصلت للمستوى {lvl_res['new_level']} وحصلت على 100 نقطة إضافية!")
                        except: pass
                
                # ═══ فحص الإنجازات ═══
                try:
                    from database.queries import tasks as tasks_q
                    tasks_q.check_achievements(uid)
                except: pass
                
            except Exception as e:
                err = f"{type(e).__name__}: {str(e)[:100]}"
                log.error(f"Scrape task {task_id} failed: {err}")
                progress.finish(task_id, "failed")
                progress.update(task_id, reason=err)
            finally:
                if cli:
                    try: await cli.disconnect()
                    except: pass
        except Exception as outer:
            log.error(f"Scrape {task_id} outer error: {outer}")
            progress.finish(task_id, "failed")
            progress.update(task_id, reason=str(outer)[:100])

    from web.app import get_pyro_loop
    import asyncio
    loop = get_pyro_loop()
    asyncio.run_coroutine_threadsafe(_do(), loop)

    return jsonify({"ok": True, "task_id": task_id})

@bp.route("/api/web/scrape/status/<task_id>")
@require_login
def scrape_status(task_id):
    uid = get_uid()
    task = progress.get(task_id)
    if not task:
        return jsonify({"error": "task not found"}), 404
    if task["user_id"] != uid and not session.get("is_owner"):
        return jsonify({"error": "forbidden"}), 403
    return jsonify(task)

@bp.route("/api/web/scrape/cancel/<task_id>", methods=["POST"])
@require_login
def scrape_cancel(task_id):
    uid = get_uid()
    task = progress.get(task_id)
    if not task:
        return jsonify({"error": "task not found"}), 404
    if task["user_id"] != uid and not session.get("is_owner"):
        return jsonify({"error": "forbidden"}), 403
    progress.cancel(task_id)
    return jsonify({"ok": True})

@bp.route("/api/web/scrape/status/all")
@require_login
def scrape_status_all():
    uid = get_uid()
    rows = db.fetchall("SELECT task_id, kind, status FROM scrape_progress WHERE user_id=? AND status='running'", (str(uid),))
    return jsonify({"tasks": [dict(r) for r in rows]})

@bp.route("/api/web/tasks/clear", methods=["POST"])
@require_login
def tasks_clear_all():
    uid = get_uid()
    db.execute("UPDATE scrape_progress SET status='failed' WHERE user_id=? AND status='running'", (str(uid),), commit=True)
    return jsonify({"ok": True})
