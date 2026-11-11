"""Admin commands"""
from pyrogram import Client, filters
from bot.middleware import owner_only
from bot.keyboards import main_menu
from database.connection import get_db
from config import config

db = get_db()

@Client.on_message(filters.command("stats") & filters.private)
@owner_only
async def stats_handler(client, message):
    users_count = db.fetchone("SELECT COUNT(*) as c FROM users")["c"]
    sessions = db.fetchone("SELECT COUNT(*) as c FROM sessions")["c"]
    members = db.fetchone("SELECT COUNT(*) as c FROM members")["c"]
    await message.reply_text(
        f"📊 <b>إحصائيات النظام</b>\n\n"
        f"👥 المستخدمين: {users_count}\n"
        f"📱 الجلسات: {sessions}\n"
        f"🗄️ الأعضاء: {members:,}",
        reply_markup=main_menu(True)
    )

@Client.on_message(filters.command("health") & filters.private)
@owner_only
async def health_handler(client, message):
    from bot.client import is_ready
    from database.connection import get_db
    db_ok = get_db().ping()
    await message.reply_text(
        f"🏥 <b>صحة النظام</b>\n\n"
        f"البوت: {'✅' if is_ready() else '❌'}\n"
        f"الداتابيز: {'✅' if db_ok else '❌'}"
    )
