"""Bot pump handler (stub)"""
from pyrogram import Client, filters
from bot.middleware import ban_check
from bot.keyboards import main_menu

@Client.on_message(filters.text & filters.private & filters.create(lambda _, __, m: m.text == "🚀 الضخ"))
@ban_check
async def pump_menu_handler(client, message):
    await message.reply_text(
        "🚀 <b>قسم الضخ</b>\n\n"
        "استخدم الموقع للبدء:\n"
        "http://127.0.0.1:8090/app",
        reply_markup=main_menu(message.from_user.id == __import__("config").config.telegram.owner_id)
    )
