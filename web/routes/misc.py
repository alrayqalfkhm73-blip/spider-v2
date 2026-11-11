"""Misc: weather, referrals, stats, settings"""
from flask import Blueprint, jsonify, request, session
from web.deps import require_login, get_uid
from database.queries import users as users_q
from database.connection import get_db
from config import config
from logger import get_logger

bp = Blueprint("misc", __name__)
log = get_logger("web.misc")
db = get_db()


@bp.route("/api/web/admin/live_stats")
@require_login
def admin_live_stats():
    from flask import session
    if not session.get("is_owner"):
        return jsonify({"error": "forbidden"}), 403
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        users = db.fetchone("SELECT COUNT(*) as c FROM users")["c"]
        members = db.fetchone("SELECT COUNT(*) as c FROM members")["c"]
        tasks = db.fetchone("SELECT COUNT(*) as c FROM scrape_progress WHERE status='running'")["c"]
        return jsonify({"cpu": cpu, "ram": ram, "users": users, "members": members, "tasks": tasks, "ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/api/web/admin/logs")
@require_login
def admin_logs():
    from flask import session
    if not session.get("is_owner"):
        return jsonify({"error": "forbidden"}), 403
    try:
        rows = db.fetchall("SELECT * FROM activity_log ORDER BY id DESC LIMIT 50")
        return jsonify({"logs": [dict(r) for r in rows]})
    except Exception:
        return jsonify({"logs": []})


@bp.route("/api/web/transfer", methods=["POST"])
@require_login
def transfer_points():
    uid = get_uid()
    data = request.json or {}
    target_id = str(data.get("target_id", "")).strip()
    amount = int(data.get("amount", 0))

    if target_id == uid:
        return jsonify({"error": "لا يمكنك التحويل لنفسك"}), 400
    if amount <= 0:
        return jsonify({"error": "الرجاء إدخال مبلغ صحيح"}), 400

    # التأكد إن المستخدم المستهدف موجود
    target_user = users_q.get_user(target_id)
    if not target_user:
        return jsonify({"error": "المستخدم المستهدف غير موجود"}), 404

    # التأكد من الرصيد
    sender = users_q.get_user(uid)
    if not sender or sender.get("points", 0) < amount:
        return jsonify({"error": "رصيدك غير كافي"}), 400

    try:
        with db.transaction():
            # خصم من المرسل
            db.execute("UPDATE users SET points = points - ? WHERE id=?", (amount, uid))
            # إضافة للمستلم
            db.execute("UPDATE users SET points = points + ? WHERE id=?", (amount, target_id))
            # تسجيل في سجل المراقبة
            db.execute("INSERT INTO activity_log (user_id, action, details, created_at) VALUES (?, ?, ?, datetime('now'))",
                       (uid, "Transfer", f"Sent {amount} to {target_id}"))
        
        # تحديث الكاش
        from database.cache import user_cache
        user_cache.invalidate(f"user:{uid}")
        user_cache.invalidate(f"user:{target_id}")
        
        return jsonify({"ok": True, "new_balance": sender.get("points", 0) - amount})
    except Exception as e:
        return jsonify({"error": str(e)[:80]}), 500


@bp.route("/api/web/failed/list")
@require_login
def failed_list():
    uid = get_uid()
    rows = db.fetchall("SELECT * FROM failed_members WHERE owner_user_id=? ORDER BY id DESC LIMIT 100", (str(uid),))
    return jsonify({"failed": [dict(r) for r in rows]})

@bp.route("/api/web/failed/clear", methods=["POST"])
@require_login
def failed_clear():
    uid = get_uid()
    db.execute("DELETE FROM failed_members WHERE owner_user_id=?", (str(uid),), commit=True)
    return jsonify({"ok": True})

@bp.route("/api/web/blacklist/list")
@require_login
def blacklist_list():
    uid = get_uid()
    rows = db.fetchall("SELECT * FROM blacklist WHERE owner_user_id=? ORDER BY id DESC LIMIT 100", (str(uid),))
    return jsonify({"blacklist": [dict(r) for r in rows]})

@bp.route("/api/web/blacklist/add", methods=["POST"])
@require_login
def blacklist_add():
    uid = get_uid()
    data = request.json or {}
    target = str(data.get("id", "")).strip()
    if target:
        db.execute("INSERT OR IGNORE INTO blacklist (id, owner_user_id, reason, added_at) VALUES (?, ?, 'manual', datetime('now'))", (target, str(uid)), commit=True)
    return jsonify({"ok": True})

@bp.route("/api/web/blacklist/remove", methods=["POST"])
@require_login
def blacklist_remove():
    uid = get_uid()
    data = request.json or {}
    target = str(data.get("id", "")).strip()
    if target:
        db.execute("DELETE FROM blacklist WHERE id=? AND owner_user_id=?", (target, str(uid)), commit=True)
    return jsonify({"ok": True})


@bp.route("/api/web/achievements/list")
@require_login
def achievements_list():
    uid = get_uid()
    from database.queries import tasks as tasks_q
    unlocked = set(tasks_q.get_achievements(uid))
    
    data = []
    for ach_id, ach in tasks_q.ACHIEVEMENTS_LIST.items():
        data.append({
            "id": ach_id, "name": ach["name"], "desc": ach["desc"],
            "icon": ach["icon"], "reward": ach["reward"],
            "unlocked": ach_id in unlocked
        })
    return jsonify({"achievements": data})


@bp.route("/api/web/support/list")
@require_login
def support_list():
    uid = get_uid()
    rows = db.fetchall("SELECT * FROM support_tickets WHERE user_id=? ORDER BY id DESC", (str(uid),))
    return jsonify({"tickets": [dict(r) for r in rows]})

@bp.route("/api/web/support/create", methods=["POST"])
@require_login
def support_create():
    uid = get_uid()
    data = request.json or {}
    msg = (data.get("message") or "").strip()
    
    if not msg:
        return jsonify({"error": "الرسالة فارغة"}), 400

    db.execute("INSERT INTO support_tickets (user_id, message, created_at) VALUES (?, ?, datetime('now'))", (str(uid), msg), commit=True)
    
    # إرسال إشعار للمالك على تليجرام
    try:
        from web.routes.telegram_webhook import notify_user
        from config import config
        notify_user(config.telegram.owner_id, f"🎫 <b>تذكرة دعم جديدة من الموقع!</b>\n\n👤 من: <code>{uid}</code>\n📝 الرسالة: {msg}\n\n(للرد، استخدم البوت)")
    except: pass

    return jsonify({"ok": True})


@bp.route("/api/web/activity_feed")
@require_login
def activity_feed():
    try:
        # بنجيب آخر 20 حركة من جدول السجلات
        rows = db.fetchall("SELECT user_id, action, details, created_at FROM activity_log ORDER BY id DESC LIMIT 20")
        return jsonify({"activities": [dict(r) for r in rows]})
    except Exception as e:
        return jsonify({"activities": [], "error": str(e)})


@bp.route("/api/web/announcements/list")
@require_login
def announcements_list():
    db.execute("CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, pinned INTEGER DEFAULT 0, created_by TEXT, created_at TEXT)", commit=True)
    rows = db.fetchall("SELECT * FROM announcements ORDER BY pinned DESC, id DESC LIMIT 50")
    return jsonify({"announcements": [dict(r) for r in rows]})

@bp.route("/api/web/announcements/create", methods=["POST"])
@require_login
def announcements_create():
    if not session.get("is_owner"):
        return jsonify({"error": "للمالك فقط"}), 403
    data = request.json or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    if not title or not content:
        return jsonify({"error": "البيانات ناقصة"}), 400
    db.execute("INSERT INTO announcements (title, content, created_by, created_at) VALUES (?, ?, ?, datetime('now'))", (title, content, str(get_uid())), commit=True)
    return jsonify({"ok": True})

@bp.route("/api/web/announcements/delete", methods=["POST"])
@require_login
def announcements_delete():
    if not session.get("is_owner"):
        return jsonify({"error": "للمالك فقط"}), 403
    data = request.json or {}
    aid = data.get("id")
    if aid:
        db.execute("DELETE FROM announcements WHERE id=?", (aid,), commit=True)
    return jsonify({"ok": True})

@bp.route("/api/web/announcements/pin", methods=["POST"])
@require_login
def announcements_pin():
    if not session.get("is_owner"):
        return jsonify({"error": "للمالك فقط"}), 403
    data = request.json or {}
    aid = data.get("id")
    if aid:
        row = db.fetchone("SELECT pinned FROM announcements WHERE id=?", (aid,))
        if row:
            new_val = 0 if row["pinned"] else 1
            db.execute("UPDATE announcements SET pinned=? WHERE id=?", (new_val, aid), commit=True)
    return jsonify({"ok": True})


@bp.route("/api/web/notifications/list")
@require_login
def notifications_list():
    db.execute("CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, title TEXT, message TEXT, is_read INTEGER DEFAULT 0, created_at TEXT)", commit=True)
    uid = get_uid()
    rows = db.fetchall("SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 20", (str(uid),))
    unread = db.fetchone("SELECT COUNT(*) as c FROM notifications WHERE user_id=? AND is_read=0", (str(uid),))["c"]
    return jsonify({"notifications": [dict(r) for r in rows], "unread": unread})

@bp.route("/api/web/notifications/read", methods=["POST"])
@require_login
def notifications_read():
    uid = get_uid()
    data = request.json or {}
    nid = data.get("id")
    if nid == "all":
        db.execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (str(uid),), commit=True)
    elif nid:
        db.execute("UPDATE notifications SET is_read=1 WHERE id=? AND user_id=?", (nid, str(uid)), commit=True)
    return jsonify({"ok": True})

@bp.route("/api/web/notifications/send", methods=["POST"])
@require_login
def notifications_send():
    if not session.get("is_owner"):
        return jsonify({"error": "للمالك فقط"}), 403
    data = request.json or {}
    target = data.get("user_id")
    title = data.get("title")
    msg = data.get("message")
    if not target or not title or not msg:
        return jsonify({"error": "بيانات ناقصة"}), 400
    db.execute("INSERT INTO notifications (user_id, title, message, created_at) VALUES (?, ?, ?, datetime('now'))", (str(target), title, msg), commit=True)
    return jsonify({"ok": True})


@bp.route("/api/web/global_chat/messages")
@require_login
def global_chat_messages():
    room = request.args.get("room", "global")
    db.execute("CREATE TABLE IF NOT EXISTS global_chat (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, message TEXT, room TEXT DEFAULT 'global', created_at TEXT)", commit=True)
    # بنتأكد إن عمود الغرفة موجود (لو الداتابيز قديمة)
    try: db.execute("ALTER TABLE global_chat ADD COLUMN room TEXT DEFAULT 'global'", commit=True)
    except: pass
    
    rows = db.fetchall("SELECT * FROM global_chat WHERE room=? ORDER BY id DESC LIMIT 50", (room,))
    return jsonify({"messages": [dict(r) for r in reversed(rows)]})

@bp.route("/api/web/global_chat/send", methods=["POST"])
@require_login
def global_chat_send():
    data = request.json or {}
    msg = (data.get("message") or "").strip()
    room = data.get("room", "global")
    if not msg:
        return jsonify({"error": "الرسالة فارغة"}), 400
    if len(msg) > 300:
        return jsonify({"error": "الرسالة طويلة جداً (300 حرف كحد أقصى)"}), 400
        
    uid = get_uid()
    # لو الغرفة VIP، نتأكد إنه VIP الأول
    if room == "vip":
        from database.queries import users as users_q
        if not session.get("is_owner") and not users_q.is_vip(uid):
            return jsonify({"error": "غير مصرح لك بالكتابة هنا"}), 403
        
    db.execute("INSERT INTO global_chat (user_id, message, room, created_at) VALUES (?, ?, ?, datetime('now'))", (str(uid), msg, room), commit=True)
    return jsonify({"ok": True})


@bp.route("/api/web/profile/update_bio", methods=["POST"])
@require_login
def update_bio():
    uid = get_uid()
    data = request.json or {}
    bio = (data.get("bio") or "").strip()
    
    if len(bio) > 150:
        return jsonify({"error": "البايو طويل جداً (150 حرف كحد أقصى)"}), 400
        
    db.execute("UPDATE users SET bio=? WHERE id=?", (bio, str(uid)), commit=True)
    return jsonify({"ok": True})


@bp.route("/api/web/leaderboard_pro")
@require_login
def leaderboard_pro():
    cat = request.args.get("cat", "points")
    order_by = {
        "points": "points DESC",
        "scraped": "total_scraped DESC",
        "pumped": "total_pumped DESC",
        "level": "level DESC, xp DESC"
    }.get(cat, "points DESC")
    
    try:
        rows = db.fetchall(f"SELECT id, points, role, total_scraped, total_pumped, level, xp FROM users ORDER BY {order_by} LIMIT 20")
        uid = get_uid()
        my_rank = None
        for i, r in enumerate(rows):
            if str(r["id"]) == str(uid):
                my_rank = i + 1
                break
        return jsonify({"leaders": [dict(r) for r in rows], "my_rank": my_rank, "category": cat})
    except Exception as e:
        return jsonify({"leaders": [], "my_rank": None, "error": str(e)})


@bp.route("/api/web/redeem", methods=["POST"])
@require_login
def redeem_code():
    from database.queries import codes as codes_q
    uid = get_uid()
    data = request.json or {}
    code = (data.get("code") or "").strip()
    if not code: return jsonify({"error": "اكتب الكود أولاً"}), 400
    
    res = codes_q.redeem(code, uid)
    if res.get("ok"):
        return jsonify({"ok": True, "value": res.get("value", 0)})
    return jsonify({"error": res.get("error", "كود غير صحيح")}), 400

@bp.route("/api/web/codes/generate", methods=["POST"])
@require_login
def generate_code():
    if not session.get("is_owner"):
        return jsonify({"error": "للمالك فقط"}), 403
    from database.queries import codes as codes_q
    data = request.json or {}
    try:
        val = int(data.get("value", 500))
    except (ValueError, TypeError):
        return jsonify({"error": "من فضلك اكتب قيمة رقمية صحيحة"}), 400
        
    if val <= 0:
        return jsonify({"error": "القيمة لازم تكون أكبر من صفر"}), 400

    try:
        codes = codes_q.create(value=val, count=1, days=30)
        if codes and len(codes) > 0:
            return jsonify({"ok": True, "code": codes[0]})
        return jsonify({"error": "فشل التوليد من الداتابيز"}), 500
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500


@bp.route("/api/web/arcade/reward", methods=["POST"])
@require_login
def arcade_reward():
    uid = get_uid()
    db.execute("CREATE TABLE IF NOT EXISTS arcade_wins (user_id TEXT, date TEXT, wins INTEGER DEFAULT 0, PRIMARY KEY(user_id, date))", commit=True)
    
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    
    row = db.fetchone("SELECT wins FROM arcade_wins WHERE user_id=? AND date=?", (str(uid), today))
    current_wins = row["wins"] if row else 0
    
    if current_wins >= 5:
        return jsonify({"error": "لقد وصلت للحد الأقصى من المكافآت اليومية (5 مرات)"}), 400
        
    db.execute("INSERT INTO arcade_wins (user_id, date, wins) VALUES (?, ?, 1) ON CONFLICT(user_id, date) DO UPDATE SET wins=wins+1", (str(uid), today), commit=True)
    
    from database.queries import users as users_q
    users_q.update_points(uid, 50)
    
    return jsonify({"ok": True, "reward": 50})


@bp.route("/api/web/calendar/status")
@require_login
def calendar_status():
    uid = str(get_uid())
    from datetime import datetime, timedelta
    db.execute("CREATE TABLE IF NOT EXISTS daily_login (user_id TEXT PRIMARY KEY, streak INTEGER DEFAULT 0, last_claim TEXT)", commit=True)
    
    row = db.fetchone("SELECT * FROM daily_login WHERE user_id=?", (uid,))
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    streak = 0
    claimed_today = False
    
    if row:
        streak = row["streak"]
        if row["last_claim"] == today:
            claimed_today = True
        elif row["last_claim"] != yesterday and row["last_claim"] is not None:
            streak = 0 # اتقطع الستريك
            
    # المكافآت: 100, 200, 300, 500, 800, 1200, 2000
    rewards = [100, 200, 300, 500, 800, 1200, 2000]
    
    return jsonify({
        "streak": streak,
        "claimed_today": claimed_today,
        "rewards": rewards,
        "next_day": (streak + 1) if not claimed_today else streak
    })

@bp.route("/api/web/calendar/claim", methods=["POST"])
@require_login
def calendar_claim():
    uid = str(get_uid())
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    
    row = db.fetchone("SELECT * FROM daily_login WHERE user_id=?", (uid,))
    if row and row["last_claim"] == today:
        return jsonify({"error": "لقد استلمت مكافأة اليوم بالفعل"}), 400
        
    current_streak = row["streak"] if row else 0
    new_streak = min(current_streak + 1, 7) # الحد الأقصى 7 أيام
    
    rewards = [100, 200, 300, 500, 800, 1200, 2000]
    reward = rewards[new_streak - 1]
    
    with db.transaction():
        db.execute("INSERT INTO daily_login (user_id, streak, last_claim) VALUES (?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET streak=?, last_claim=?", 
                   (uid, new_streak, today, new_streak, today))
        
        from database.queries import users as users_q
        users_q.update_points(uid, reward)
        
    return jsonify({"ok": True, "reward": reward, "new_streak": new_streak})


@bp.route("/api/web/users/public_profile")
@require_login
def public_profile():
    target_id = request.args.get("uid", "").strip()
    if not target_id:
        return jsonify({"error": "اكتب ID المستخدم أولاً"}), 400
        
    from database.queries import users as users_q
    from config import config
    
    u = users_q.get_user(target_id)
    if not u:
        return jsonify({"error": "هذا المستخدم غير موجود"}), 404
        
    # إرجاع البيانات العامة فقط (بدون أي بيانات حساسة)
    data = {
        "id": u["id"],
        "points": u.get("points", 0),
        "level": u.get("level", 1),
        "xp": u.get("xp", 0),
        "role": u.get("role", "USER"),
        "badge": u.get("badge", ""),
        "bio": u.get("bio", ""),
        "total_scraped": u.get("total_scraped", 0),
        "total_pumped": u.get("total_pumped", 0),
        "gift_streak": u.get("gift_streak", 0),
        "is_owner": (str(u["id"]) == str(config.telegram.owner_id))
    }
    return jsonify({"ok": True, "user": data})


@bp.route("/api/web/system/status")
@require_login
def system_status():
    if not session.get("is_owner"):
        return jsonify({"error": "للمالك فقط"}), 403
    try:
        import psutil
        import os
        import time
        from database.connection import get_db
        db = get_db()
        
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        
        # حجم الداتابيز
        from config import config
        db_size = 0
        if config.paths.db_path.exists():
            db_size = config.paths.db_path.stat().st_size / (1024 * 1024) # بالميجا
            
        # وقت التشغيل
        boot_time = psutil.boot_time()
        uptime_sec = time.time() - boot_time
        days = int(uptime_sec // (24 * 3600))
        hours = int((uptime_sec % (24 * 3600)) // 3600)
        uptime_str = f"{days} يوم و {hours} ساعة"
        
        users = db.fetchone("SELECT COUNT(*) as c FROM users")["c"]
        members = db.fetchone("SELECT COUNT(*) as c FROM members")["c"]
        active_tasks = db.fetchone("SELECT COUNT(*) as c FROM scrape_progress WHERE status='running'")["c"]
        
        return jsonify({
            "ok": True,
            "cpu": cpu,
            "ram": ram,
            "db_size_mb": round(db_size, 2),
            "uptime": uptime_str,
            "users": users,
            "members": members,
            "active_tasks": active_tasks
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/web/admin/user_manage", methods=["POST"])
@require_login
def admin_user_manage():
    if not session.get("is_owner"):
        return jsonify({"error": "للمالك فقط"}), 403
        
    data = request.json or {}
    target_id = str(data.get("target_id", "")).strip()
    action = data.get("action")
    value = data.get("value")
    
    if not target_id:
        return jsonify({"error": "ID المستخدم مطلوب"}), 400
        
    from database.queries import users as users_q
    user = users_q.get_user(target_id)
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404
        
    try:
        if action == "add_points":
            users_q.update_points(target_id, int(value))
        elif action == "remove_points":
            users_q.update_points(target_id, -int(value))
        elif action == "make_vip":
            users_q.set_role(target_id, "VIP", 30)
        elif action == "ban":
            users_q.ban_user(target_id, "admin_action", 0)
        elif action == "unban":
            users_q.unban_user(target_id)
            
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


MAINTENANCE_MODE = {"active": False}

@bp.route("/api/web/admin/control/status")
@require_login
def control_status():
    return jsonify({"maintenance": MAINTENANCE_MODE["active"]})

@bp.route("/api/web/admin/control/maintenance", methods=["POST"])
@require_login
def control_maintenance():
    if not session.get("is_owner"):
        return jsonify({"error": "للمالك فقط"}), 403
    data = request.json or {}
    MAINTENANCE_MODE["active"] = bool(data.get("active"))
    return jsonify({"ok": True, "maintenance": MAINTENANCE_MODE["active"]})

@bp.route("/api/web/admin/control/broadcast", methods=["POST"])
@require_login
def control_broadcast():
    if not session.get("is_owner"):
        return jsonify({"error": "للمالك فقط"}), 403
    data = request.json or {}
    msg = data.get("message")
    if not msg:
        return jsonify({"error": "الرسالة فارغة"}), 400
        
    users = db.fetchall("SELECT id FROM users")
    import requests, time
    from config import config
    success = 0
    for u in users:
        try:
            r = requests.post(f"https://api.telegram.org/bot{config.telegram.bot_token}/sendMessage", 
                              data={"chat_id": u["id"], "text": f"📢 <b>رسالة من الإدارة:</b>\n\n{msg}", "parse_mode": "HTML"}, timeout=5)
            if r.status_code == 200: success += 1
        except: pass
        time.sleep(0.05) # حماية من الحظر
    return jsonify({"ok": True, "sent": success})

@bp.route("/api/web/admin/control/backup")
@require_login
def control_backup():
    if not session.get("is_owner"):
        return jsonify({"error": "للمالك فقط"}), 403
    from flask import send_file
    from config import config
    return send_file(config.paths.db_path, as_attachment=True, download_name="spider_backup.db")

@bp.route("/api/web/admin/control/clear_cache", methods=["POST"])
@require_login
def control_clear_cache():
    if not session.get("is_owner"):
        return jsonify({"error": "للمالك فقط"}), 403
    from database.cache import user_cache, stats_cache
    user_cache.invalidate()
    stats_cache.invalidate()
    return jsonify({"ok": True})


@bp.route("/api/web/my_activity")
@require_login
def my_activity():
    uid = get_uid()
    try:
        rows = db.fetchall("SELECT action, details, created_at FROM activity_log WHERE user_id=? ORDER BY id DESC LIMIT 50", (str(uid),))
        return jsonify({"activities": [dict(r) for r in rows]})
    except Exception as e:
        return jsonify({"activities": [], "error": str(e)})


@bp.route("/api/web/vip/lounge/status")
@require_login
def vip_lounge_status():
    uid = get_uid()
    from database.queries import users as users_q
    user = users_q.get_user(uid)
    is_owner = session.get("is_owner")
    is_vip = users_q.is_vip(uid) if user else False
    
    if not is_owner and not is_vip:
        return jsonify({"error": "هذه الصالة لكبار الزوار VIP فقط"}), 403
        
    db.execute("CREATE TABLE IF NOT EXISTS vip_daily (user_id TEXT PRIMARY KEY, last_claim TEXT)", commit=True)
    row = db.fetchone("SELECT * FROM vip_daily WHERE user_id=?", (str(uid),))
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    claimed = (row and row["last_claim"] == today)
    
    return jsonify({"ok": True, "is_vip": True, "claimed_today": claimed})

@bp.route("/api/web/vip/lounge/claim", methods=["POST"])
@require_login
def vip_lounge_claim():
    uid = get_uid()
    from database.queries import users as users_q
    is_owner = session.get("is_owner")
    if not is_owner and not users_q.is_vip(uid):
        return jsonify({"error": "للمالك أو VIP فقط"}), 403
        
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    
    row = db.fetchone("SELECT * FROM vip_daily WHERE user_id=?", (str(uid),))
    if row and row["last_claim"] == today:
        return jsonify({"error": "لقد استلمت هدية الـ VIP اليوم"}), 400
        
    db.execute("INSERT OR REPLACE INTO vip_daily (user_id, last_claim) VALUES (?, ?)", (str(uid), today), commit=True)
    users_q.update_points(uid, 500)
    
    return jsonify({"ok": True, "reward": 500})


@bp.route("/api/web/inventory")
@require_login
def get_inventory():
    uid = get_uid()
    user = db.fetchone("SELECT * FROM users WHERE id=?", (str(uid),))
    if not user: return jsonify({"error": "not found"}), 404
    
    # ═══ إصلاح المشكلة: تحويل البيانات لـ Dictionary عشان نستخدم .get() ═══
    user_dict = dict(user)
    
    theme_row = db.fetchone("SELECT value FROM user_settings WHERE user_id=? AND key='theme'", (str(uid),))
    theme = theme_row["value"] if theme_row else "default"
    
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        db.execute("CREATE TABLE IF NOT EXISTS arcade_wins (user_id TEXT, date TEXT, wins INTEGER DEFAULT 0, PRIMARY KEY(user_id, date))", commit=True)
        arcade_row = db.fetchone("SELECT wins FROM arcade_wins WHERE user_id=? AND date=?", (str(uid), today))
        arcade_wins = arcade_row["wins"] if arcade_row else 0
    except Exception:
        arcade_wins = 0
    
    return jsonify({
        "ok": True,
        "badge": user_dict.get("badge") or "",
        "role": user_dict.get("role") or "USER",
        "vip_expiry": user_dict.get("vip_expiry") or "",
        "theme": theme,
        "level": user_dict.get("level") or 1,
        "xp": user_dict.get("xp") or 0,
        "points": user_dict.get("points") or 0,
        "arcade_wins": arcade_wins,
        "referrals": user_dict.get("referral_count") or 0
    }), 404
    
    theme_row = db.fetchone("SELECT value FROM user_settings WHERE user_id=? AND key='theme'", (str(uid),))
    theme = theme_row["value"] if theme_row else "default"
    
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    
    # ═══ إصلاح: التأكد من إنشاء الجدول لو مش موجود ═══
    try:
        db.execute("CREATE TABLE IF NOT EXISTS arcade_wins (user_id TEXT, date TEXT, wins INTEGER DEFAULT 0, PRIMARY KEY(user_id, date))", commit=True)
        arcade_row = db.fetchone("SELECT wins FROM arcade_wins WHERE user_id=? AND date=?", (str(uid), today))
        arcade_wins = arcade_row["wins"] if arcade_row else 0
    except Exception:
        arcade_wins = 0
    
    return jsonify({
        "ok": True,
        "badge": user.get("badge", ""),
        "role": user.get("role", "USER"),
        "vip_expiry": user.get("vip_expiry", ""),
        "theme": theme,
        "level": user.get("level", 1),
        "xp": user.get("xp", 0),
        "points": user.get("points", 0),
        "arcade_wins": arcade_wins,
        "referrals": user.get("referral_count", 0)
    })


@bp.route("/api/web/auctions/list")
@require_login
def auctions_list():
    db.execute("CREATE TABLE IF NOT EXISTS auctions (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, item_type TEXT, item_value TEXT, start_price INTEGER, current_bid INTEGER DEFAULT 0, current_bidder TEXT, end_time TEXT, status TEXT DEFAULT 'ACTIVE')", commit=True)
    rows = db.fetchall("SELECT * FROM auctions WHERE status='ACTIVE' ORDER BY id DESC")
    
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # فحص المزادات المنتهية
    for r in rows:
        if r["end_time"] < now:
            db.execute("UPDATE auctions SET status='COMPLETED' WHERE id=?", (r["id"],), commit=True)
            if r["current_bidder"]:
                # تسليم الجايزة
                if r["item_type"] == "points":
                    from database.queries import users as users_q
                    users_q.update_points(r["current_bidder"], int(r["item_value"]))
                elif r["item_type"] == "vip":
                    from database.queries import users as users_q
                    users_q.set_role(r["current_bidder"], "VIP", int(r["item_value"]))
                elif r["item_type"] == "badge":
                    db.execute("UPDATE users SET badge=? WHERE id=?", (r["item_value"], r["current_bidder"]), commit=True)
    
    rows = db.fetchall("SELECT * FROM auctions WHERE status='ACTIVE' ORDER BY id DESC")
    return jsonify({"auctions": [dict(r) for r in rows]})

@bp.route("/api/web/auctions/bid", methods=["POST"])
@require_login
def auctions_bid():
    uid = get_uid()
    data = request.json or {}
    auc_id = data.get("id")
    bid_amount = int(data.get("amount", 0))
    
    auc = db.fetchone("SELECT * FROM auctions WHERE id=? AND status='ACTIVE'", (auc_id,))
    if not auc: return jsonify({"error": "المزاد غير موجود أو انتهى"}), 404
    
    current_bid = auc["current_bid"] or auc["start_price"]
    if bid_amount <= current_bid:
        return jsonify({"error": f"يجب أن تكون مزايدتك أعلى من {current_bid}"}), 400
        
    from database.queries import users as users_q
    user = users_q.get_user(uid)
    
    # لو المستخدم هو أعلى مزايد بالفعل، بنحسب الفرق بس
    if auc["current_bidder"] == str(uid):
        diff = bid_amount - (auc["current_bid"] or 0)
    else:
        diff = bid_amount
        
    if not session.get("is_owner") and user["points"] < diff:
        return jsonify({"error": "رصيدك غير كافي للمزايدة"}), 400
        
    with db.transaction():
        # خصم من المزايد الجديد
        if not session.get("is_owner"):
            users_q.update_points(uid, -diff)
            
        # إرجاع النقاط للمزايد القديم
        if auc["current_bidder"] and auc["current_bidder"] != str(uid):
            users_q.update_points(auc["current_bidder"], auc["current_bid"])
            
        db.execute("UPDATE auctions SET current_bid=?, current_bidder=? WHERE id=?", (bid_amount, str(uid), auc_id), commit=True)
        
    return jsonify({"ok": True})

@bp.route("/api/web/auctions/create", methods=["POST"])
@require_login
def auctions_create():
    if not session.get("is_owner"): return jsonify({"error": "للمالك فقط"}), 403
    data = request.json or {}
    
    from datetime import datetime, timedelta
    end_time = (datetime.now() + timedelta(hours=int(data.get("hours", 1)))).strftime("%Y-%m-%d %H:%M:%S")
    
    db.execute("INSERT INTO auctions (title, item_type, item_value, start_price, end_time) VALUES (?, ?, ?, ?, ?)",
               (data.get("title"), data.get("item_type"), data.get("item_value"), int(data.get("start_price")), end_time), commit=True)
    return jsonify({"ok": True})


@bp.route("/api/web/ai_memory/list")
@require_login
def ai_memory_list():
    uid = get_uid()
    try:
        rows = db.fetchall("SELECT id, role, content, created_at FROM ai_context WHERE user_id=? ORDER BY id DESC LIMIT 50", (str(uid),))
        return jsonify({"memory": [dict(r) for r in reversed(rows)]})
    except Exception as e:
        return jsonify({"memory": [], "error": str(e)})

@bp.route("/api/web/ai_memory/delete", methods=["POST"])
@require_login
def ai_memory_delete():
    uid = get_uid()
    data = request.json or {}
    mid = data.get("id")
    if mid:
        db.execute("DELETE FROM ai_context WHERE id=? AND user_id=?", (mid, str(uid)), commit=True)
    return jsonify({"ok": True})

@bp.route("/api/web/ai_memory/clear", methods=["POST"])
@require_login
def ai_memory_clear():
    uid = get_uid()
    try:
        from ai import memory
        memory.clear(uid)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/api/web/weather")
@require_login
def weather():
    city = request.args.get("city", "Cairo")
    coords = {
        "Cairo": (30.0444, 31.2357), "Alexandria": (31.2001, 29.9187),
        "Riyadh": (24.7136, 46.6753), "Dubai": (25.2048, 55.2708),
        "London": (51.5074, -0.1278), "Paris": (48.8566, 2.3522),
    }
    lat, lon = coords.get(city, (30.0444, 31.2357))
    try:
        import httpx
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        r = httpx.get(url, timeout=8)
        if r.status_code != 200:
            return jsonify({"error": "فشل الاتصال"}), 500
        cur = r.json().get("current", {})
        return jsonify({
            "text": f"{city}: {cur.get('temperature_2m','?')}°C · رطوبة {cur.get('relative_humidity_2m','?')}% · رياح {cur.get('wind_speed_10m','?')} كم/س",
            "temp": cur.get("temperature_2m"),
        })
    except Exception as e:
        return jsonify({"error": str(e)[:80]}), 500

@bp.route("/api/web/referrals")
@require_login
def referrals():
    uid = get_uid()
    user = users_q.get_user(uid)
    count = user.get("referral_count", 0) if user else 0
    return jsonify({
        "link": f"https://t.me/spider_bot?start={uid}",
        "count": count, "bonus": 10
    })

@bp.route("/api/web/stats/chart")
@require_login
def stats_chart():
    from datetime import datetime, timedelta
    labels, data = [], []
    for i in range(6, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        labels.append(d[5:])
        try:
            n = db.fetchone("SELECT COUNT(*) as c FROM members WHERE scraped_at LIKE ?", (d + "%",))["c"]
            data.append(n)
        except: data.append(0)
    return jsonify({"labels": labels, "data": data})

@bp.route("/api/settings/all")
@require_login
def settings_all():
    uid = get_uid()
    try:
        rows = db.fetchall("SELECT key, value FROM user_settings WHERE user_id=?", (uid,))
        return jsonify({"settings": {r["key"]: r["value"] for r in rows}})
    except:
        return jsonify({"settings": {}})

@bp.route("/api/settings/toggle", methods=["POST"])
@require_login
def settings_toggle():
    """Alias for set (preview.html uses this)"""
    uid = get_uid()
    data = request.json or {}
    key = (data.get("key") or "").strip()
    value = str(data.get("value", ""))
    if not key: return jsonify({"error": "key مطلوب"}), 400
    try:
        db.execute("INSERT OR REPLACE INTO user_settings (user_id, key, value) VALUES (?, ?, ?)",
                   (uid, key, value), commit=True)
        return jsonify({"ok": True, "key": key, "value": value})
    except Exception as e:
        return jsonify({"error": str(e)[:80]}), 500

@bp.route("/api/settings/set", methods=["POST"])
@require_login
def settings_set():
    uid = get_uid()
    data = request.json or {}
    key = (data.get("key") or "").strip()
    value = str(data.get("value", ""))
    if not key: return jsonify({"error": "key مطلوب"}), 400
    try:
        db.execute("INSERT OR REPLACE INTO user_settings (user_id, key, value) VALUES (?, ?, ?)",
                   (uid, key, value), commit=True)
        return jsonify({"ok": True, "key": key, "value": value})
    except Exception as e:
        return jsonify({"error": str(e)[:80]}), 500
