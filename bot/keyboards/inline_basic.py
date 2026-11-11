"""Inline Keyboards — الأساسية (start, status, updates, lang, VIP, voice, schedule)"""
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def _ikb(rows: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(rows)


# ═══════════════════════════════════════════════════════════
# 🏠 Start Menu (بعد /start)
# ═══════════════════════════════════════════════════════════
def start_inline_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("🤖 المساعد", callback_data="start_ai"),
         InlineKeyboardButton("🎁 الهدية", callback_data="start_gift")],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data="start_stats"),
         InlineKeyboardButton("💳 شحن", callback_data="start_charge")],
    ])


# ═══════════════════════════════════════════════════════════
# 📋 Status Categories (للمالك)
# ═══════════════════════════════════════════════════════════
def status_categories() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("🤖 أدوات الذكاء الاصطناعي", callback_data="st_cat_ai")],
        [InlineKeyboardButton("🎯 الأدوات التفاعلية", callback_data="st_cat_ui")],
        [InlineKeyboardButton("👑 أدوات المالك", callback_data="st_cat_owner")],
        [InlineKeyboardButton("📅 نظام التحديثات", callback_data="st_cat_updates")],
    ])


def status_back() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("↩️ رجوع", callback_data="st_back")],
    ])


# ═══════════════════════════════════════════════════════════
# 🚀 Feature Flags
# ═══════════════════════════════════════════════════════════
def flags_control() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("✅ تفعيل كل الـ 22 ميزة", callback_data="flags_activate_all")],
        [InlineKeyboardButton("🔒 قفل الكل (وضع اختبار)", callback_data="flags_deactivate_all")],
        [InlineKeyboardButton("📋 عرض الحالة التفصيلية", callback_data="flags_show")],
    ])


# ═══════════════════════════════════════════════════════════
# ➕ Add Update — features toggles (ديناميكي)
# ═══════════════════════════════════════════════════════════
def add_update_menu(selected: list = None) -> InlineKeyboardMarkup:
    selected = selected or []
    features = [
        ("ai", "المساعد الذكي"),
        ("interactive", "الأزرار التفاعلية"),
        ("charts", "الرسم البياني"),
        ("updates", "التحديثات القادمة"),
        ("scrape", "تحسين السحب"),
        ("fixes", "إصلاحات وأخطاء"),
    ]
    rows = []
    for fid, fname in features:
        icon = "✅" if fid in selected else "⬜"
        rows.append([InlineKeyboardButton(f"{icon} {fname}", callback_data=f"upd_tog_{fid}")])
    rows.append([InlineKeyboardButton("📝 إضافة نص مخصص", callback_data="upd_custom_text")])
    rows.append([InlineKeyboardButton("✅ تأكيد وجدولة للخميس", callback_data="upd_confirm")])
    return _ikb(rows)


# ═══════════════════════════════════════════════════════════
# 🌐 Languages (12 لغة)
# ═══════════════════════════════════════════════════════════
def languages_keyboard(current: str = "ar") -> InlineKeyboardMarkup:
    from bot.keyboards.constants import LANGUAGES
    items = list(LANGUAGES.items())
    rows = []
    for i in range(0, len(items), 2):
        row = []
        for code, name in items[i:i + 2]:
            check = "✅ " if code == current else ""
            row.append(InlineKeyboardButton(f"{check}{name}", callback_data=f"lang_{code}"))
        rows.append(row)
    return _ikb(rows)


# ═══════════════════════════════════════════════════════════
# 💎 VIP Store
# ═══════════════════════════════════════════════════════════
def vip_store() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("💎 يوم VIP - 500", callback_data="vip_buy_1_500")],
        [InlineKeyboardButton("💎 3 أيام VIP - 1200", callback_data="vip_buy_3_1200")],
        [InlineKeyboardButton("💎 أسبوع VIP - 2500", callback_data="vip_buy_7_2500")],
    ])


# ═══════════════════════════════════════════════════════════
# 🎙️ Voice Selection
# ═══════════════════════════════════════════════════════════
def voice_selection() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("👨 راجل (Shakir)", callback_data="v_set_ar-EG-ShakirNeural")],
        [InlineKeyboardButton("👩 ست (Salma)", callback_data="v_set_ar-EG-SalmaNeural")],
        [InlineKeyboardButton("👦 طفل (Hamed)", callback_data="v_set_ar-EG-HamedNeural")],
    ])


# ═══════════════════════════════════════════════════════════
# ⏰ Schedule Scrape
# ═══════════════════════════════════════════════════════════
def schedule_scrape() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("12 منتصف الليل", callback_data="cron_scrape_0")],
        [InlineKeyboardButton("3 الفجر", callback_data="cron_scrape_3")],
        [InlineKeyboardButton("6 صباحاً", callback_data="cron_scrape_6")],
        [InlineKeyboardButton("إيقاف", callback_data="cron_scrape_off")],
    ])


# ═══════════════════════════════════════════════════════════
# 🔍 Member Filters
# ═══════════════════════════════════════════════════════════
def member_filters(username_on: bool = False, active_on: bool = False) -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton(
            f"👤 يوزر نيم فقط: {'✅' if username_on else '❌'}",
            callback_data="filt_toggle_username")],
        [InlineKeyboardButton(
            f"⚡ نشط (30 يوم): {'✅' if active_on else '❌'}",
            callback_data="filt_toggle_active")],
        [InlineKeyboardButton("✅ حفظ", callback_data="filt_save")],
    ])


# ═══════════════════════════════════════════════════════════
# 📱 Session Selection (dynamically built in real handler)
# ═══════════════════════════════════════════════════════════
def session_selection(sessions: list = None) -> InlineKeyboardMarkup:
    """sessions: list of {name, status}"""
    rows = []
    if sessions:
        for s in sessions:
            mark = "🟢" if s.get("status") == "ACTIVE" else "⚪"
            rows.append([InlineKeyboardButton(
                f"{mark} {s['name'][:40]}",
                callback_data=f"set_sess_{s['name']}")])
    return _ikb(rows)


def session_details(name: str) -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("🔄 تعطيل/تفعيل", callback_data=f"tog_sess_{name}")],
        [InlineKeyboardButton("✏️ إعادة تسمية", callback_data=f"ren_sess_{name}")],
        [InlineKeyboardButton("🔍 فحص", callback_data=f"chk_sess_{name}")],
    ])


# ═══════════════════════════════════════════════════════════
# 🎯 Proxy binding to session
# ═══════════════════════════════════════════════════════════
def proxy_binding(proxies: list = None, session: str = "") -> InlineKeyboardMarkup:
    """proxies: list of {id, proxy_string, quality_score}"""
    rows = []
    if proxies:
        for p in proxies[:15]:
            q = p.get("quality_score", 50)
            ps = p.get("proxy_string", "")
            rows.append([InlineKeyboardButton(
                f"Q:{q} {ps[:30]}",
                callback_data=f"bind_{session}_{p['id']}")])
    rows.append([InlineKeyboardButton("🗑️ حذف الكل", callback_data="clear_bindings")])
    return _ikb(rows)


# ═══════════════════════════════════════════════════════════
# 🎮 Arcade games menu
# ═══════════════════════════════════════════════════════════
def arcade_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("❌⭕ إكس أو (Tic Tac Toe)", callback_data="game_ttt")],
        [InlineKeyboardButton("🧠 كويز المعلومات", callback_data="game_trivia")],
        [InlineKeyboardButton("🔢 مبارزة الأرقام", callback_data="game_hl")],
        [InlineKeyboardButton("❌ إنهاء الألعاب", callback_data="game_exit")],
    ])


def tic_tac_toe_board(board: list, game_over: bool = False) -> InlineKeyboardMarkup:
    """board: list of 9 items ('' | 'X' | 'O')"""
    rows = []
    for r in range(3):
        row = []
        for c in range(3):
            idx = r * 3 + c
            v = board[idx]
            text = "⬜" if v == "" else ("❌" if v == "X" else "⭕")
            cb = "ttt_played" if (v or game_over) else f"ttt_{idx}"
            row.append(InlineKeyboardButton(text, callback_data=cb))
        rows.append(row)
    if game_over:
        rows.append([
            InlineKeyboardButton("🔄 العب تاني", callback_data="game_ttt"),
            InlineKeyboardButton("🚪 خروج", callback_data="game_back"),
        ])
    else:
        rows.append([InlineKeyboardButton("🚪 خروج", callback_data="game_back")])
    return _ikb(rows)


def higher_lower_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("⬆️ أعلى", callback_data="hl_higher"),
         InlineKeyboardButton("⬇️ أقل", callback_data="hl_lower")],
    ])


# ═══════════════════════════════════════════════════════════
# ⚙️ Pump delay settings
# ═══════════════════════════════════════════════════════════
def pump_delay_settings() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("⚡ سريع 10-20ث", callback_data="pump_set_10_20"),
         InlineKeyboardButton("🚀 توربو 5-10ث", callback_data="pump_set_5_10")],
        [InlineKeyboardButton("⚖️ عادي 30-60ث", callback_data="pump_set_30_60"),
         InlineKeyboardButton("🛡️ آمن 60-90ث", callback_data="pump_set_60_90")],
        [InlineKeyboardButton("🎨 مخصص (اكتب)", callback_data="pump_set_custom")],
        [InlineKeyboardButton("🔄 رجوع للافتراضي", callback_data="pump_set_reset")],
    ])


# ═══════════════════════════════════════════════════════════
# 📊 Scrape settings
# ═══════════════════════════════════════════════════════════
def scrape_settings(username_only: bool = False) -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("📊 تغيير الحد اليومي", callback_data="scrape_set_cap")],
        [InlineKeyboardButton(
            f"👤 username only: {'✅' if username_only else '❌'}",
            callback_data="scrape_toggle_uonly")],
    ])


# ═══════════════════════════════════════════════════════════
# ✉️ Feedback types
# ═══════════════════════════════════════════════════════════
def feedback_types() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("💡 اقتراح", callback_data="fb_suggestion")],
        [InlineKeyboardButton("🐛 بلاغ باج", callback_data="fb_bug")],
        [InlineKeyboardButton("😠 شكوى", callback_data="fb_complaint")],
    ])


# ═══════════════════════════════════════════════════════════
# 🌐 Web portal (new)
# ═══════════════════════════════════════════════════════════
def web_portal(url: str) -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("🌐 دخول الموقع", url=f"{url}/app")],
        [InlineKeyboardButton("🔄 تغيير الباسورد", callback_data="web_change_pass")],
    ])
