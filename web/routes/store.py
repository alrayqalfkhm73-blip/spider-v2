"""Store endpoints — Full Functional (VIP, Themes, Badges)"""
from flask import Blueprint, jsonify, request, session
from web.deps import require_login, get_uid
from database.queries import users as users_q
from database.connection import get_db
from logger import get_logger

bp = Blueprint("store", __name__)
log = get_logger("web.store")
db = get_db()

THEMES = {
    "light": 500, "amoled": 500, "midnight": 500, "sakura": 500, "ocean": 500,
    "royal": 1000, "cyber": 1000, "sunset": 1000, "forest": 1000, "crimson": 1000,
    "luxury_gold": 1500, "neon": 1500, "ice": 1500, "lavender": 1500, "toxic": 1500,
    "matrix": 2000, "blood": 2000, "desert": 2000, "arctic": 2000, "space": 2000,
    "emerald": 2500, "ruby": 2500, "sapphire": 2500, "copper": 2500, "platinum": 2500,
    "obsidian": 3000, "candy": 3000, "mint": 3000, "peach": 3000, "galaxy": 3000
}

BADGES = {
    "king": 50000, "millionaire": 25000, "warrior": 10000,
    "legend": 15000, "wolf": 5000
}

@bp.route("/api/web/store/vip", methods=["POST"])
@require_login
def store_vip():
    uid = get_uid()
    data = request.json or {}
    days = int(data.get("days", 1))
    price = int(data.get("price", 500))

    user = users_q.get_user(uid)
    if not user: return jsonify({"error": "مستخدم غير موجود"}), 404
    
    is_owner = session.get("is_owner")
    if not is_owner and user.get("points", 0) < price:
        return jsonify({"error": f"رصيدك {user.get('points', 0)} غير كافي"}), 400

    if not is_owner:
        users_q.update_points(uid, -price)
        
    users_q.set_role(uid, "VIP", days)
    log.info(f"VIP purchase: {uid} {days} days")
    
    new_bal = 999999999 if is_owner else user.get("points", 0) - price
    return jsonify({"ok": True, "days": days, "new_balance": new_bal})

@bp.route("/api/web/store/theme", methods=["POST"])
@require_login
def store_theme():
    uid = get_uid()
    data = request.json or {}
    theme = (data.get("theme") or "").strip()

    if theme not in THEMES:
        return jsonify({"error": "سمة غير معروفة"}), 400
    price = THEMES[theme]

    user = users_q.get_user(uid)
    if not user: return jsonify({"error": "مستخدم غير موجود"}), 404
    
    is_owner = session.get("is_owner")
    if not is_owner and user.get("points", 0) < price:
        return jsonify({"error": f"رصيدك {user.get('points', 0)} غير كافي"}), 400

    if not is_owner:
        users_q.update_points(uid, -price)
        
    try:
        db.execute("INSERT OR REPLACE INTO user_settings (user_id, key, value) VALUES (?, 'theme', ?)", (uid, theme), commit=True)
    except: pass
    
    log.info(f"Theme purchase: {uid} {theme}")
    new_bal = 999999999 if is_owner else user.get("points", 0) - price
    return jsonify({"ok": True, "theme": theme, "new_balance": new_bal})

@bp.route("/api/web/store/badge", methods=["POST"])
@require_login
def store_badge():
    uid = get_uid()
    data = request.json or {}
    badge = (data.get("badge") or "").strip()

    if badge not in BADGES:
        return jsonify({"error": "شارة غير معروفة"}), 400
    price = BADGES[badge]

    user = users_q.get_user(uid)
    if not user: return jsonify({"error": "مستخدم غير موجود"}), 404
    
    is_owner = session.get("is_owner")
    if not is_owner and user.get("points", 0) < price:
        return jsonify({"error": f"رصيدك {user.get('points', 0)} غير كافي"}), 400

    if not is_owner:
        users_q.update_points(uid, -price)
        
    db.execute("UPDATE users SET badge=? WHERE id=?", (badge, uid), commit=True)
    log.info(f"Badge purchase: {uid} {badge}")
    
    new_bal = 999999999 if is_owner else user.get("points", 0) - price
    return jsonify({"ok": True, "badge": badge, "new_balance": new_bal})

@bp.route("/api/web/store/points", methods=["POST"])
@require_login
def store_points():
    return jsonify({"ok": True, "message": "بوابة الدفع قادمة قريباً"}), 200


@bp.route("/api/web/store/gift", methods=["POST"])
@require_login
def store_gift():
    uid = get_uid()
    data = request.json or {}
    item_type = data.get("type") # vip, theme, badge
    item_id = data.get("item_id")
    target_id = str(data.get("target_id", "")).strip()
    price = int(data.get("price", 0))
    
    if not target_id or not item_type:
        return jsonify({"error": "بيانات ناقصة"}), 400
        
    if target_id == str(uid):
        return jsonify({"error": "مينفعش تهدي نفسك!"}), 400
        
    target_user = users_q.get_user(target_id)
    if not target_user:
        return jsonify({"error": "المستخدم اللي بتحاول تهديه غير موجود"}), 404
        
    is_owner = session.get("is_owner")
    sender = users_q.get_user(uid)
    if not is_owner and sender.get("points", 0) < price:
        return jsonify({"error": f"رصيدك {sender.get('points', 0)} غير كافي لإهداء هذه الهدية"}), 400
        
    # الخصم من المُهدي
    if not is_owner:
        users_q.update_points(uid, -price)
        
    # التطبيق على المُهدى له
    if item_type == "vip":
        users_q.set_role(target_id, "VIP", 30) # افتراضي 30 يوم للهدية
    elif item_type == "theme":
        db.execute("INSERT OR REPLACE INTO user_settings (user_id, key, value) VALUES (?, 'theme', ?)", (target_id, item_id), commit=True)
    elif item_type == "badge":
        db.execute("UPDATE users SET badge=? WHERE id=?", (item_id, target_id), commit=True)
        
    # إشعار للمُهدى له
    try:
        db.execute("INSERT INTO notifications (user_id, title, message, created_at) VALUES (?, ?, ?, datetime('now'))", 
                   (target_id, "🎁 هدية جديدة!", f"لقد أهداك المستخدم {uid} هدية: {item_id}"))
        from web.routes.telegram_webhook import notify_user
        notify_user(target_id, f"🎁 <b>هدية جديدة!</b>\nلقد أهداك المستخدم <code>{uid}</code> هدية: <b>{item_id}</b>.")
    except: pass
    
    new_bal = 999999999 if is_owner else sender.get("points", 0) - price
    return jsonify({"ok": True, "new_balance": new_bal})

@bp.route("/api/web/store/themes")
def list_themes():
    return jsonify({"themes": THEMES})
