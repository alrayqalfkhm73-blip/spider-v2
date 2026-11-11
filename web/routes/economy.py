"""Economy: tasks, wheel, box, achievements, leaderboard"""
from flask import Blueprint, jsonify, request
from web.deps import require_login, get_uid
from database.queries import tasks as tasks_q, users as users_q
from database.connection import get_db
from logger import get_logger

bp = Blueprint("economy", __name__)
log = get_logger("web.economy")
db = get_db()

@bp.route("/api/web/tasks")
@require_login
def tasks_list():
    uid = get_uid()
    return jsonify({"tasks": tasks_q.get_daily(uid)})

@bp.route("/api/web/tasks/claim", methods=["POST"])
@require_login
def tasks_claim():
    uid = get_uid()
    data = request.json or {}
    tid = (data.get("task_id") or "").strip()
    if not tid: return jsonify({"error": "task_id مطلوب"}), 400
    return jsonify(tasks_q.claim(uid, tid))

@bp.route("/api/web/wheel/spin", methods=["POST"])
@require_login
def wheel_spin():
    uid = get_uid()
    return jsonify(tasks_q.wheel_spin(uid))

@bp.route("/api/web/daily_box", methods=["POST"])
@require_login
def daily_box():
    uid = get_uid()
    return jsonify(tasks_q.daily_box(uid))

@bp.route("/api/web/achievements")
@require_login
def achievements():
    uid = get_uid()
    unlocked = set(tasks_q.get_achievements(uid))
    all_ach = [
        {"id": "first_login", "name": "الخطوة الأولى", "desc": "أول تسجيل دخول"},
        {"id": "first_scrape", "name": "صياد اليوزرات", "desc": "أول سحب"},
        {"id": "rich", "name": "ألفير", "desc": "10000 نقطة"},
        {"id": "vip", "name": "الملكي", "desc": "شراء VIP"},
        {"id": "wheel_win", "name": "المحظوظ", "desc": "فوز في العجلة"},
    ]
    for a in all_ach:
        a["unlocked"] = a["id"] in unlocked
    return jsonify({"achievements": all_ach})

@bp.route("/api/web/leaderboard")
@require_login
def leaderboard():
    return jsonify({"leaders": users_q.get_top_users(10)})
