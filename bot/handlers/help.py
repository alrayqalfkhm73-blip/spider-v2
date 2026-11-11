"""/help and /id"""
from pyrogram import Client, filters
from bot.texts import fmt
from bot.keyboards import main_menu
from bot.middleware import ban_check
from config import config

@Client.on_message(filters.command("help") & filters.private)
@ban_check
async def help_handler(client, message):
    uid = message.from_user.id
    is_owner = (uid == config.telegram.owner_id)
    await message.reply_text(fmt("help"), reply_markup=main_menu(is_owner))

@Client.on_message(filters.command("id") & filters.private)
async def id_handler(client, message):
    uid = message.from_user.id
    await message.reply_text(f"🆔 <code>{uid}</code>")
