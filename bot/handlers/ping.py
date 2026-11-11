"""Ping command — diagnostic"""
from pyrogram import Client, filters

@Client.on_message(filters.command("ping") & filters.private)
async def ping_handler(client, message):
    print(f"[PING] received from {message.from_user.id}")
    await message.reply_text("🏓 **Pong!** البوت شغال ✓")
