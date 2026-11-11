"""Bot scrape handler (stub for now)"""
from pyrogram import Client, filters
from bot.middleware import ban_check
from bot.keyboards import main_menu
from bot.texts import E

@Client.on_message(filters.text & filters.private & filters.create(lambda _, __, m: m.text == "🕷️ السحب"))
@ban_check
async def scrape_menu_handler(client, message):
    await message.reply_text(
        "🕷️ <b>قسم السحب</b>\n\n"
        "استخدم الموقع للبدء في السحب:\n"
        "http://127.0.0.1:8090/app\n\n"
        "(الميزة هتتفعل بالكامل في النسخة النهائية)",
        reply_markup=main_menu(message.from_user.id == __import__("config").config.telegram.owner_id)
    )
