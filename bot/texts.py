"""كل نصوص البوت"""

E = {
    "spider": "🕷️", "rocket": "🚀", "crown": "👑", "star": "⭐",
    "gift": "🎁", "wheel": "🎡", "trophy": "🏆", "check": "✅",
    "cross": "❌", "warn": "⚠️", "lock": "🔒", "gear": "⚙️",
    "help": "ℹ️", "user": "👤", "money": "💰", "chart": "📊",
}

TEXTS = {
    "welcome": (
        "<b>🕷️ أهلاً بك في Spider V2</b>\n\n"
        "أنا بوت المنظومة الشاملة.\n"
        "👤 <b>اسمك:</b> {name}\n"
        "🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
        "اختر من القائمة بالأسفل 👇"
    ),
    "welcome_owner": (
        "<b>👑 أهلاً بك يا قائد</b>\n\n"
        "أنت المالك. عندك صلاحيات كاملة.\n"
        "🆔 <code>{user_id}</code>"
    ),
    "referral_bonus": "🎁 تم تسجيلك عبر رابط إحالة! صديقك حصل على +10 نقاط.",
    "welcome_bonus": "🎁 مبروك! حصلت على +10 نقاط ترحيبية.",
    "banned": "🚫 أنت محظور من استخدام البوت.",
    "maintenance": "🕒 البوت في وضع الصيانة حالياً. جرب بعد شوية.",
    "admin_only": "👑 الأمر ده للمالك فقط.",
    "help": (
        "<b>ℹ️ المساعدة</b>\n\n"
        "<b>الأوامر المتاحة:</b>\n"
        "/start — البداية\n"
        "/help — هذه القائمة\n"
        "/stats — إحصائياتك\n"
        "/id — عرض ID بتاعك\n\n"
        "للتواصل مع المالك اضغط على زر المساعدة."
    ),
    "menu_greeting": "من القائمة بالأسفل اختار:",
    "back": "↩️ رجوع",
}

def fmt(key: str, **kwargs) -> str:
    """استبدال متغيرات في النص"""
    text = TEXTS.get(key, key)
    try:
        return text.format(**kwargs)
    except KeyError:
        return text
