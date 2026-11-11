"""/api/web/me"""
from flask import Blueprint, jsonify, session
from web.deps import require_login, get_uid
from database.queries import users

bp = Blueprint("me", __name__)

@bp.route("/api/web/me")
@require_login
def api_me():
    uid = get_uid()
    from database.queries import users
    streak_data = users.check_streak(uid)
    user = users.get_user(uid)
    if not user:
        users.ensure_user(uid)
        from database.queries import users
    streak_data = users.check_streak(uid)
    user = users.get_user(uid)

    return jsonify({
        "id": uid,
        "points": (user.get("points", 0) if user else 0),
        "role": (user.get("role", "USER") if user else "USER"),
        "is_owner": bool(session.get("is_owner")),
        "streak": streak_data.get("streak", 0),
        "streak_reward": streak_data.get("reward", 0),
        "streak_already": streak_data.get("already", False)
    })
