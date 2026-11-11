"""Bot AI chat handler"""
from pyrogram import Client, filters, enums
from bot.middleware import ban_check
from bot.keyboards import main_menu
from ai.router import ask
from config import config

# Menu items that should NOT trigger AI chat
MENU_TEXTS = {
    "🕷️ السحب", "🚀 الضخ", "📱 الجلسات", "🌐 البروكسيات",
    "💰 المحفظة", "🎁 الهدية", "🎡 العجلة", "🏆 المتصدرين",
    "⚙️ الإعدادات", "ℹ️ المساعدة", "↩️ رجوع",
    "📊 إحصائيات النظام", "📢 بث رسالة",
    "🕒 وضع الصيانة", "🔙 رجوع",
}

@Client.on_message(filters.text & filters.private)
@ban_check
async def ai_chat_handler(client, message):
    text = message.text.strip()
    if not text or text.startswith("/") or text in MENU_TEXTS:
        return

    uid = message.from_user.id
    is_owner = (uid == config.telegram.owner_id)
    await message.reply_chat_action(enums.ChatAction.TYPING)

    try:
        result = await ask(text, str(uid), is_owner, mode="fast")
        reply = result.get("reply", "معرفتش أرد")
        await message.reply_text(reply, reply_markup=main_menu(is_owner))
    except Exception as e:
        await message.reply_text(f"حصل خطأ: {str(e)[:80]}")
