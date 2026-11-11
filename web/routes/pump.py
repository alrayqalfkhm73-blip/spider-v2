"""Pump API — Clean Version with XP & Achievements"""
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from web.deps import require_login, get_uid
from database.queries import sessions as sess_q
from database.connection import get_db
from scraper import progress
from scraper.pump_engine import run_pump
from logger import get_logger

bp = Blueprint("pump", __name__)
log = get_logger("web.pump")
db = get_db()

@bp.route("/api/web/pump/start", methods=["POST"])
@require_login
def pump_start():
    uid = get_uid()
    data = request.json or {}
    target = data.get("chat_id")
    mode = data.get("mode", "safe")

    if not target:
        return jsonify({"error": "chat_id مطلوب"}), 400

    active = progress.user_active_tasks(uid)
    if active:
        return jsonify({"error": f"فيه عملية شغالة ({active[0]})"}), 429

    task_id = progress.create("pump", uid, str(target))

    async def _do():
        from pyrogram import Client
        from config import config
        import asyncio
        
        try:
            all_sess = sess_q.get_all(uid)
            actives = [s for s in all_sess if s.get("status") == "ACTIVE"]
            
            if not actives:
                pool_sessions = all_sess[0] if all_sess else None
            else:
                actives.sort(key=lambda x: x.get("daily_pumped", 0))
                pool_sessions = actives[0]
                
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
                
                stats = await run_pump(cli, target, uid, task_id, mode)
                
                # ═══ إضافة الخبرة (XP) ═══
                if stats.get("success", 0) > 0:
                    xp_amount = stats["success"] * 5
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
                progress.finish(task_id, "failed")
                progress.update(task_id, reason=err)
            finally:
                if cli:
                    try: await cli.disconnect()
                    except: pass
        except Exception as outer:
            progress.finish(task_id, "failed")
            progress.update(task_id, reason=str(outer)[:100])

    from web.app import get_pyro_loop
    import asyncio
    loop = get_pyro_loop()
    asyncio.run_coroutine_threadsafe(_do(), loop)

    return jsonify({"ok": True, "task_id": task_id})

@bp.route("/api/web/pump/status/<task_id>")
@require_login
def pump_status(task_id):
    uid = get_uid()
    task = progress.get(task_id)
    if not task:
        return jsonify({"error": "task not found"}), 404
    if task["user_id"] != uid and not session.get("is_owner"):
        return jsonify({"error": "forbidden"}), 403
    
    try:
        all_sess = sess_q.get_all(uid)
        today = datetime.now().strftime("%Y-%m-%d")
        total_used = sum(s["daily_pumped"] for s in all_sess if s["last_pump_date"] == today)
        max_limit = len(all_sess) * 20
        task["session_limit"] = {"used": total_used, "max": max_limit if max_limit > 0 else 20}
    except: 
        pass
    
    return jsonify(task)
