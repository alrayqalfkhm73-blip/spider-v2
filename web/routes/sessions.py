import asyncio
"""Sessions endpoints — Pyrogram Worker (safe + persistent)"""
from flask import Blueprint, jsonify, request
from web.deps import require_login, get_uid
from database.queries import sessions as sess_q
from database.connection import get_db
from config import config
from logger import get_logger

bp = Blueprint("sessions_web", __name__)
log = get_logger("web.sessions")
db = get_db()

# Pending bindings: uid -> {phone, hash, sess_name, client}
_pending = {}

@bp.route("/api/web/sessions/list")
@require_login
def list_sessions():
    uid = get_uid()
    rows = sess_q.get_all(uid)
    out = []
    db_names = set()
    from pathlib import Path
    
    # 1. من DB
    for r in rows:
        name = str(r["session_name"]).replace(".session", "")
        db_names.add(name)
        p = config.paths.sessions_dir / f"{name}.session"
        out.append({
            "name": name,
            "status": r.get("status", "UNKNOWN"),
            "size": p.stat().st_size if p.exists() else 0,
            "exists": p.exists(),
            "added_at": r.get("added_at"),
            "in_db": True,
        })
    
    # 2. من الديسك (ملفات مش مسجلة في DB)
    try:
        if config.paths.sessions_dir.exists():
            for p in config.paths.sessions_dir.glob(f"{uid}_*.session"):
                name = p.stem
                if name not in db_names and p.stat().st_size > 1000:
                    out.append({
                        "name": name,
                        "status": "UNLINKED",
                        "size": p.stat().st_size,
                        "exists": True,
                        "added_at": None,
                        "in_db": False,
                    })
    except Exception as e:
        log.warning(f"disk scan failed: {e}")
    
    return jsonify({"sessions": out})

@bp.route("/api/web/sessions/add", methods=["POST"])
@require_login
def add_session():
    uid = get_uid()
    data = request.json or {}
    phone = (data.get("phone") or "").strip().replace(" ", "")

    if not phone.startswith("+") or len(phone) < 10:
        return jsonify({"error": "الرقم لازم يبدأ بـ + ويكون 10 أرقام على الأقل"}), 400

    from web.app import run_pyro
    import asyncio

    async def _do():
        from pyrogram import Client
        sess_name = f"{uid}_{phone.replace('+', '')}"
        sess_path = str(config.paths.sessions_dir / sess_name)
        cli = Client(
            sess_path,
            api_id=config.telegram.api_id,
            api_hash=config.telegram.api_hash,
            device_model="Samsung SM-S918B",
            system_version="SDK 34",
            app_version="10.6.1",
            lang_code="ar",
            in_memory=False,
        )
        try:
            await cli.connect()
            code_info = await cli.send_code(phone)
            _pending[uid] = {
                "phone": phone,
                "hash": code_info.phone_code_hash,
                "sess_name": sess_name,
                "cli": cli,
            }
            log.info(f"Code sent to {phone[:4]}*** for {uid}")
            return {"ok": True, "message": "تم إرسال الكود — افتح تليجرام واكتبه"}
        except Exception as e:
            try: await cli.disconnect()
            except: pass
            err = str(e)
            log.error(f"add_session failed: {err[:100]}")
            if "FLOOD" in err.upper():
                return {"error": "تليجرام طلب انتظار. جرب بعد دقيقة."}
            if "PHONE_NUMBER_INVALID" in err.upper():
                return {"error": "الرقم غلط. اكتبه بصيغة دولية +2010..."}
            if "PHONE_NUMBER_BANNED" in err.upper():
                return {"error": "الرقم ده محظور من تليجرام"}
            return {"error": f"خطأ: {err[:80]}"}

    result = run_pyro(_do(), timeout=40)
    if not isinstance(result, dict):
        return jsonify({"error": "خطأ داخلي"}), 500
    if result.get("ok"):
        return jsonify(result)
    return jsonify(result), 400

@bp.route("/api/web/sessions/verify", methods=["POST"])
@require_login
def verify_session():
    uid = get_uid()
    data = request.json or {}
    code = (data.get("code") or "").strip().replace(" ", "")

    if not code:
        return jsonify({"error": "اكتب الكود أولاً"}), 400

    pending = _pending.get(uid)
    if not pending:
        return jsonify({"error": "مفيش عملية ربط جارية. ابدأ من جديد."}), 400

    from web.app import run_pyro

    async def _do():
        cli = pending["cli"]
        try:
            await cli.sign_in(pending["phone"], pending["hash"], code)
            me = await cli.get_me()
            await cli.disconnect()
            await asyncio.sleep(0.5)
            # Save to DB
            sess_q.add(uid, pending["sess_name"], pending["sess_name"])
            return {"ok": True, "name": me.first_name if me else "?", "user_id": me.id if me else None}
        except Exception as e:
            try: await cli.disconnect()
            except: pass
            err = str(e)
            log.error(f"verify_session failed: {err[:100]}")
            if "PASSWORD" in err.upper():
                return {"error": "الحساب عليه تحقق بخطوتين (2FA) — مش مدعوم بعد"}
            if "PHONE_CODE_INVALID" in err.upper():
                return {"error": "الكود غلط. جرب تاني."}
            if "PHONE_CODE_EXPIRED" in err.upper():
                _pending.pop(uid, None)
                return {"error": "الكود انتهت صلاحيته. ابدأ من جديد."}
            return {"error": f"خطأ: {err[:80]}"}

    import asyncio
    result = run_pyro(_do(), timeout=40)
    if not isinstance(result, dict):
        return jsonify({"error": "خطأ داخلي"}), 500
    if result.get("ok"):
        _pending.pop(uid, None)
        return jsonify(result)
    return jsonify(result), 400


@bp.route("/api/web/sessions/set_active", methods=["POST"])
@require_login
def set_active_session():
    uid = get_uid()
    data = request.json or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name مطلوب"}), 400
    
    sess = sess_q.get_by_name(name)
    if not sess:
        # لو الملف موجود على الديسك بس مش في DB - نسجله الأول
        from pathlib import Path as _P
        sess_file = config.paths.sessions_dir / f"{name}.session"
        if sess_file.exists() and str(uid) in name:
            sess_q.add(uid, name, name)
        else:
            return jsonify({"error": "الجلسة مش موجودة"}), 404
    elif str(sess.get("user_id")) != uid:
        return jsonify({"error": "الجلسة دي مش بتاعتك"}), 403
    
    try:
        db.execute("UPDATE sessions SET status='INACTIVE' WHERE user_id=?", (uid,), commit=True)
        db.execute("UPDATE sessions SET status='ACTIVE' WHERE user_id=? AND session_name=?", (uid, name), commit=True)
        
        # ✅ تصفير كاش الجروبات عشان تتحدث فوراً
        try:
            from web.routes import scrape_more
            scrape_more._groups_cache.clear()
            log.info("Groups cache cleared after session switch")
        except Exception as e:
            log.warning(f"cache clear failed: {e}")
        
        log.info(f"Active session → {name} for {uid}")
        return jsonify({"ok": True, "active": name})
    except Exception as e:
        log.error(f"set_active failed: {e}")
        return jsonify({"error": str(e)[:80]}), 500


@bp.route("/api/web/sessions/get_active")
@require_login
def get_active_session():
    uid = get_uid()
    active = sess_q.get_active(uid)
    return jsonify({
        "active": active["session_name"] if active else None
    })




@bp.route("/api/web/sessions/all")
@require_login
def all_sessions():
    """للمالك فقط: يعرض كل الجلسات لكل المستخدمين"""
    from flask import session as flask_session
    if not flask_session.get("is_owner"):
        return jsonify({"error": "للمالك فقط"}), 403

    try:
        rows = db.fetchall("SELECT session_name, user_id, status, added_at FROM sessions ORDER BY added_at DESC")
        out = []
        for r in rows:
            name = str(r["session_name"]).replace(".session", "")
            p = config.paths.sessions_dir / f"{name}.session"
            out.append({
                "name": name,
                "user_id": r.get("user_id"),
                "status": r.get("status", "UNKNOWN"),
                "size": p.stat().st_size if p.exists() else 0,
                "exists": p.exists(),
                "added_at": r.get("added_at"),
            })
        return jsonify({"sessions": out})
    except Exception as e:
        return jsonify({"error": str(e)[:80]}), 500


@bp.route("/api/web/sessions/delete", methods=["POST"])
@require_login
def delete_session():
    uid = get_uid()
    data = request.json or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name مطلوب"}), 400
    sess = sess_q.get_by_name(name)
    if not sess or str(sess.get("user_id")) != uid:
        return jsonify({"error": "مش موجودة أو مش بتاعتك"}), 404
    sess_q.remove(name, str(config.paths.sessions_dir / name))
    return jsonify({"ok": True})
