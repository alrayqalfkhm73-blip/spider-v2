"""/start handler"""
from pyrogram import Client, filters
from bot.texts import fmt, E
from bot.keyboards import main_menu
from bot.middleware import ban_check, maintenance_check
from database.queries import users
from config import config
from logger import get_logger

log = get_logger("bot.start")

@Client.on_message(filters.command("start") & filters.private)
@ban_check
async def start_handler(client, message):
    uid = message.from_user.id
    log.info(f"[start_handler] RECEIVED /start from {uid}")
    name = message.from_user.first_name or "صديق"
    is_owner = (uid == config.telegram.owner_id)

    # استخراج المُحيل إن وجد
    referrer = None
    if len(message.text.split()) > 1:
        try:
            referrer = message.text.split()[1]
            if referrer == str(uid):
                referrer = None  # مش يحيل نفسه
        except: pass

    existing = users.get_user(uid)
    is_new = existing is None

    user = users.ensure_user(uid)
    log.info(f"/start from {uid} ({name}) new={is_new}")

    if is_new:
        if referrer and users.get_user(referrer):
            users.update_points(uid, 10)
            users.increment_stat(referrer, "referral_count")
            users.update_points(referrer, 10)
            await message.reply_text(fmt("referral_bonus"))
        else:
            users.update_points(uid, 10)
            await message.reply_text(fmt("welcome_bonus"))

    key = "welcome_owner" if is_owner else "welcome"
    text = fmt(key, name=name, user_id=uid)

    await message.reply_text(text, reply_markup=main_menu(is_owner))
    return True
