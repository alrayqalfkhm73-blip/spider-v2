"""Menu handler — يلتقط كل الأزرار ويوجهها"""
from pyrogram import Client, filters
from bot.keyboards import (
    main_menu, user_menu, get_start_menu, assistant_keyboard,
    scrape_menu, pump_menu, sessions_menu, proxies_menu,
    users_menu, marketing_menu, system_menu, tools_menu,
    stats_menu, ai_tools_menu,
)
from bot.keyboards.constants import t, get_lang_key, TRANS
from bot.middleware import ban_check
from config import config
from logger import get_logger

log = get_logger("bot.menu")

# ═══════════════════════════════════════════════════════════
# استخراج كل الأزرار من الـ menus (بشكل ديناميكي)
# ═══════════════════════════════════════════════════════════
def _get_all_button_texts() -> set:
    """يجمع كل نصوص الأزرار من كل الـ menus"""
    texts = set()
    
    # User menu
    try:
        kb = user_menu("0")
        for row in kb.keyboard:
            for btn in row:
                texts.add(btn.text)
    except: pass
    
    # Owner menu
    try:
        kb = main_menu()
        for row in kb.keyboard:
            for btn in row:
                texts.add(btn.text)
    except: pass
    
    # Submenus
    for fn in [scrape_menu, pump_menu, sessions_menu, proxies_menu,
               users_menu, marketing_menu, system_menu, tools_menu, stats_menu]:
        try:
            kb = fn()
            for row in kb.keyboard:
                for btn in row:
                    texts.add(btn.text)
        except: pass
    
    return texts


# استخراج مرة واحدة عند التحميل
ALL_MENU_TEXTS = _get_all_button_texts()
log.info(f"Menu handler loaded with {len(ALL_MENU_TEXTS)} button texts")


# ═══════════════════════════════════════════════════════════
# خريطة: زر → submenu (لو موجود)
# ═══════════════════════════════════════════════════════════
SUBMENUS = {
    "🕷️ السحب": scrape_menu,
    "🚀 الضخ": pump_menu,
    "📱 الجلسات": sessions_menu,
    "🌐 البروكسيات": proxies_menu,
    "👥 المستخدمين": users_menu,
    "🎁 التسويق": marketing_menu,
    "⚙️ النظام": system_menu,
    "🛠️ الأدوات": tools_menu,
    "📊 الإحصائيات": stats_menu,
    "🛠️ أدوات المساعد": lambda: ai_tools_menu("0"),
}


# ═══════════════════════════════════════════════════════════
# Helper: يرجع للقائمة الرئيسية
# ═══════════════════════════════════════════════════════════
def _home(user_id) -> str:
    return "🏠 القائمة الرئيسية:"


# ═══════════════════════════════════════════════════════════
# Handler الرئيسي — يلتقط كل الأزرار
# ═══════════════════════════════════════════════════════════
@Client.on_message(filters.text & filters.private)
@ban_check
async def menu_handler(client, message):
    """يلتقط أي زر من الـ menus"""
    text = (message.text or "").strip()
    uid = message.from_user.id
    is_owner = (uid == config.telegram.owner_id)
    uid_str = str(uid)

    # لو مش من أزرار القوائم → سيبها لـ handlers تانية
    if text.startswith("/"):
        return  # commands handled by command handlers
    if text not in ALL_MENU_TEXTS:
        return
    
    log.info(f"[Menu] {uid} clicked: {text}")

    # ═══ 1. الرجوع ═══
    if text in ("↩️ رجوع", "🔙 رجوع"):
        await message.reply_text(_home(uid), reply_markup=get_start_menu(uid))
        return
    
    # ═══ 2. المساعدة ═══
    if text == "ℹ️ مساعدة":
        help_text = (
            "<b>ℹ️ المساعدة</b>\n\n"
            "<b>الأوامر:</b>\n"
            "/start — البداية\n"
            "/help — هذه القائمة\n"
            "/id — ID بتاعك\n\n"
            "للتواصل مع المالك اضغط زر المساعدة."
        )
        await message.reply_text(help_text, reply_markup=get_start_menu(uid))
        return
    
    # ═══ 3. المحفظة ═══
    if text == "💰 محفظتي":
        from database.queries import users
        user = users.get_user(uid_str)
        pts = (user.get("points", 0) if user else 0)
        role = (user.get("role", "USER") if user else "USER")
        await message.reply_text(
            f"💰 <b>محفظتك</b>\n\n"
            f"💎 الرصيد: <b>{pts:,}</b> نقطة\n"
            f"👑 الرتبة: {role}",
            reply_markup=get_start_menu(uid)
        )
        return
    
    # ═══ 4. Submenu — لو الزر بيفتح قائمة فرعية ═══
    if text in SUBMENUS:
        try:
            kb = SUBMENUS[text]()
            await message.reply_text(f"<b>{text}</b>", reply_markup=kb)
        except Exception as e:
            log.error(f"Submenu error: {e}")
            await message.reply_text(f"⚠️ خطأ في فتح {text}", reply_markup=get_start_menu(uid))
        return
    
    # ═══ 5. لأي زر تاني — placeholder ═══
    await message.reply_text(
        f"<b>{text}</b>\n\n"
        f"⏳ <i>هذه الميزة قيد التطوير — ستُفعّل قريباً</i>",
        reply_markup=get_start_menu(uid)
    )
