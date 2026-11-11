"""Telegram Webhook — Simple Portal Only"""
from flask import Blueprint, request, jsonify
from logger import get_logger
import requests, json, sys, hashlib
sys.path.insert(0, "/root/spider_v2")

from config import config
from database.queries import users as users_q
from database.connection import get_db

bp = Blueprint("telegram_webhook", __name__)
log = get_logger("web.telegram_webhook")
db = get_db()

WEB_URL = "https://mockup-photo-unboxed.ngrok-free.dev/app"
USER_STATES = {}

def _api(token, method, **data):
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/{method}", data=data, timeout=15)
        return r.json()
    except Exception as e:
        log.error(f"API {method}: {e}")
        return {"ok": False}

def _send_text(token, chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup: data["reply_markup"] = json.dumps(reply_markup)
    return _api(token, "sendMessage", **data)

def get_web_keyboard():
    return {
        "keyboard": [[{"text": "🌐 بوابة الموقع"}]],
        "resize_keyboard": True,
        "is_persistent": True
    }

def _handle_message(msg, token):
    text = (msg.get("text") or "").strip()
    user = msg.get("from", {})
    uid = str(user.get("id"))
    chat_id = msg.get("chat", {}).get("id")
    first_name = user.get("first_name", "صديق")

    log.info(f"[main] from {uid}: {text[:60]!r}")

    # استقبال الباسورد
    if USER_STATES.get(uid) == "waiting_for_password":
        pwd_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        try:
            users_q.ensure_user(uid)
            db.execute("UPDATE users SET web_password=? WHERE id=?", (pwd_hash, uid), commit=True)
            USER_STATES.pop(uid, None)
            _send_text(token, chat_id, f"✅ <b>تم إنشاء كلمة المرور بنجاح!</b>\n\nالرابط: {WEB_URL}\n🆔 ID: <code>{uid}</code>\n🔑 الباسورد: (اللي كتبته حالاً)", reply_markup=get_web_keyboard())
        except Exception as e:
            _send_text(token, chat_id, f"❌ خطأ: {e}", reply_markup=get_web_keyboard())
        return

    # أمر البدء
    if text == "/start" or text.startswith("/start "):
        try: users_q.ensure_user(uid)
        except: pass
        msg = f"👋 أهلاً بك يا <b>{first_name}</b> في <b>Spider AI</b>!\n🆔 ID: <code>{uid}</code>\n\nاضغط على الزر بالأسفل للدخول للموقع."
        _send_text(token, chat_id, msg, reply_markup=get_web_keyboard())
        return

    # زرار بوابة الموقع
    if text == "🌐 بوابة الموقع":
        user = users_q.get_user(uid)
        if user and user.get("web_password"):
            _send_text(token, chat_id, f"🌐 <b>بوابة الموقع</b>\n\nالرابط: {WEB_URL}\n🆔 ID: <code>{uid}</code>\n🔑 الباسورد: (اللي مسجل قبل كده)", reply_markup=get_web_keyboard())
        else:
            USER_STATES[uid] = "waiting_for_password"
            _send_text(token, chat_id, "أنت جديد! أرسل <b>كلمة المرور الجديدة</b> الآن في الشات لحفظها:", reply_markup=get_web_keyboard())
        return

    # أي رسالة تانية
    _send_text(token, chat_id, "⚠️ يرجى الضغط على زر بوابة الموقع.", reply_markup=get_web_keyboard())

@bp.route("/webhook/telegram/main", methods=["POST"])
def webhook_main():
    data = request.json or {}
    try:
        if "message" in data: _handle_message(data["message"], config.telegram.bot_token)
        return jsonify({"ok": True}), 200
    except Exception as e:
        log.error(f"Webhook error: {e}")
        return jsonify({"ok": False}), 200
