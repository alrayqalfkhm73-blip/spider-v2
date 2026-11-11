"""/api/health — فحص الصحة"""
from flask import Blueprint, jsonify, session
from database.connection import get_db

bp = Blueprint("health", __name__)
db = get_db()

@bp.route("/api/health")
def api_health():
    db_ok = db.ping()
    return jsonify({
        "status": "ok" if db_ok else "degraded",
        "db": db_ok,
    })

@bp.route("/api/health/detail")
def api_health_detail():
    if not session.get("is_owner"):
        return jsonify({"error": "forbidden"}), 403

    db_ok = db.ping()

    try:
        from bot.client import is_ready
        bot_ok = is_ready()
    except Exception:
        bot_ok = False

    try:
        users_count = db.fetchone("SELECT COUNT(*) as c FROM users")["c"]
        sessions_count = db.fetchone("SELECT COUNT(*) as c FROM sessions")["c"]
        members_count = db.fetchone("SELECT COUNT(*) as c FROM members")["c"]
    except Exception:
        users_count = sessions_count = members_count = 0

    return jsonify({
        "status": "ok",
        "db": db_ok,
        "bot": bot_ok,
        "users": users_count,
        "sessions": sessions_count,
        "members": members_count,
    })
