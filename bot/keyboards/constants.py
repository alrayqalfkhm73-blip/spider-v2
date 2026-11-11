"""كل الثوابت — من main.py القديم
 الـ dicts والـ lists اللي بتتغذى منها الأزرار
"""

# ═══════════════════════════════════════════════════════════
# اللغات المدعومة (12)
# ═══════════════════════════════════════════════════════════
LANGUAGES = {
    "ar": "🇪🇬 العربية",
    "en": "🇬🇧 English",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "de": "🇩🇪 Deutsch",
    "ru": "🇷🇺 Русский",
    "tr": "🇹🇷 Türkçe",
    "hi": "🇮🇳 हिन्दी",
    "pt": "🇵🇹 Português",
    "it": "🇮🇹 Italiano",
    "zh": "🇨🇳 中文",
    "ja": "🇯🇵 日本語",
}

# ═══════════════════════════════════════════════════════════
# الترجمات (لـ 25 مفتاح × 12 لغة = 300 ترجمة)
# ═══════════════════════════════════════════════════════════
TRANS = {
    "scrape": {
        "ar": "🕷️ السحب", "en": "🕷️ Scrape", "fr": "🕷️ Scraper",
        "es": "🕷️ Scrapear", "de": "🕷️ Scrapen", "ru": "🕷️ Парсинг",
        "tr": "🕷️ Kazıma", "hi": "🕷️ स्क्रैप", "pt": "🕷️ Scrapar",
        "it": "🕷️ Scraping", "zh": "🕷️ 抓取", "ja": "🕷️ スクレイプ",
    },
    "pump": {
        "ar": "🚀 الضخ", "en": "🚀 Pump", "fr": "🚀 Pomper",
        "es": "🚀 Bombear", "de": "🚀 Pumpen", "ru": "🚀 Накачка",
        "tr": "🚀 Pompala", "hi": "🚀 पंप", "pt": "🚀 Bombear",
        "it": "🚀 Pompare", "zh": "🚀 泵送", "ja": "🚀 ポンプ",
    },
    "sessions": {
        "ar": "📱 الجلسات", "en": "📱 Sessions", "fr": "📱 Sessions",
        "es": "📱 Sesiones", "de": "📱 Sitzungen", "ru": "📱 Сессии",
        "tr": "📱 Oturumlar", "hi": "📱 सत्र", "pt": "📱 Sessões",
        "it": "📱 Sessioni", "zh": "📱 会话", "ja": "📱 セッション",
    },
    "proxies": {
        "ar": "🌐 البروكسيات", "en": "🌐 Proxies", "fr": "🌐 Proxys",
        "es": "🌐 Proxies", "de": "🌐 Proxys", "ru": "🌐 Прокси",
        "tr": "🌐 Proxy", "hi": "🌐 प्रॉक्सी", "pt": "🌐 Proxies",
        "it": "🌐 Proxy", "zh": "🌐 代理", "ja": "🌐 プロキシ",
    },
    "gift": {
        "ar": "🎁 الهدية اليومية", "en": "🎁 Daily Gift", "fr": "🎁 Cadeau Quotidien",
        "es": "🎁 Regalo Diario", "de": "🎁 Tägliches Geschenk", "ru": "🎁 Ежедневный Подарок",
        "tr": "🎁 Günlük Hediye", "hi": "🎁 दैनिक उपहार", "pt": "🎁 Presente Diário",
        "it": "🎁 Regalo Giornaliero", "zh": "🎁 每日礼物", "ja": "🎁 デイリーギフト",
    },
    "wheel": {
        "ar": "🎰 عجلة الحظ", "en": "🎰 Lucky Wheel", "fr": "🎰 Roue de Chance",
        "es": "🎰 Rueda de Suerte", "de": "🎰 Glücksrad", "ru": "🎰 Колесо Удачи",
        "tr": "🎰 Çarkıfelek", "hi": "🎰 भाग्य चक्र", "pt": "🎰 Roda da Sorte",
        "it": "🎰 Ruota Fortuna", "zh": "🎰 幸运轮盘", "ja": "🎰 ラッキーホイール",
    },
    "leaderboard": {
        "ar": "🏆 المتصدرين", "en": "🏆 Leaderboard", "fr": "🏆 Classement",
        "es": "🏆 Clasificación", "de": "🏆 Rangliste", "ru": "🏆 Рейтинг",
        "tr": "🏆 Liderlik", "hi": "🏆 लीडरबोर्ड", "pt": "🏆 Classificação",
        "it": "🏆 Classifica", "zh": "🏆 排行榜", "ja": "🏆 リーダーボード",
    },
    "profile": {
        "ar": "👤 ملفي", "en": "👤 Profile", "fr": "👤 Profil",
        "es": "👤 Perfil", "de": "👤 Profil", "ru": "👤 Профиль",
        "tr": "👤 Profilim", "hi": "👤 प्रोफ़ाइल", "pt": "👤 Perfil",
        "it": "👤 Profilo", "zh": "👤 资料", "ja": "👤 プロフィール",
    },
    "referrals": {
        "ar": "👥 الإحالات", "en": "👥 Referrals", "fr": "👥 Parrainages",
        "es": "👥 Referidos", "de": "👥 Empfehlungen", "ru": "👥 Рефералы",
        "tr": "👥 Davetler", "hi": "👥 रेफरल", "pt": "👥 Indicações",
        "it": "👥 Referenze", "zh": "👥 推荐", "ja": "👥 紹介",
    },
    "wallet": {
        "ar": "💰 محفظتي", "en": "💰 Wallet", "fr": "💰 Portefeuille",
        "es": "💰 Cartera", "de": "💰 Wallet", "ru": "💰 Кошелёк",
        "tr": "💰 Cüzdanım", "hi": "💰 वॉलेट", "pt": "💰 Carteira",
        "it": "💰 Portafoglio", "zh": "💰 钱包", "ja": "💰 ウォレット",
    },
    "mystats": {
        "ar": "📊 إحصائياتي", "en": "📊 My Stats", "fr": "📊 Mes Stats",
        "es": "📊 Mis Estadísticas", "de": "📊 Meine Statistiken", "ru": "📊 Моя Статистика",
        "tr": "📊 İstatistiklerim", "hi": "📊 मेरे आंकड़े", "pt": "📊 Minhas Estatísticas",
        "it": "📊 Le Mie Statistiche", "zh": "📊 我的数据", "ja": "📊 マイ統計",
    },
    "ai": {
        "ar": "🤖 المساعد الذكي", "en": "🤖 Smart Assistant", "fr": "🤖 Assistant Intelligent",
        "es": "🤖 Asistente Inteligente", "de": "🤖 KI-Assistent", "ru": "🤖 Умный Помощник",
        "tr": "🤖 Akıllı Asistan", "hi": "🤖 स्मार्ट सहायक", "pt": "🤖 Assistente Inteligente",
        "it": "🤖 Assistente Intelligente", "zh": "🤖 智能助手", "ja": "🤖 スマートアシスタント",
    },
    "general_ai": {
        "ar": "🤖 المساعد العام", "en": "🤖 General Assistant", "fr": "🤖 Assistant Général",
        "es": "🤖 Asistente General", "de": "🤖 Allg. Assistent", "ru": "🤖 Общий Помощник",
        "tr": "🤖 Genel Asistan", "hi": "🤖 सामान्य सहायक", "pt": "🤖 Assistente Geral",
        "it": "🤖 Assistente Generale", "zh": "🤖 通用助手", "ja": "🤖 汎用アシスタント",
    },
    "help": {
        "ar": "ℹ️ مساعدة", "en": "ℹ️ Help", "fr": "ℹ️ Aide",
        "es": "ℹ️ Ayuda", "de": "ℹ️ Hilfe", "ru": "ℹ️ Помощь",
        "tr": "ℹ️ Yardım", "hi": "ℹ️ सहायता", "pt": "ℹ️ Ajuda",
        "it": "ℹ️ Aiuto", "zh": "ℹ️ 帮助", "ja": "ℹ️ ヘルプ",
    },
    "back": {
        "ar": "↩️ رجوع", "en": "↩️ Back", "fr": "↩️ Retour",
        "es": "↩️ Atrás", "de": "↩️ Zurück", "ru": "↩️ Назад",
        "tr": "↩️ Geri", "hi": "↩️ पीछे", "pt": "↩️ Voltar",
        "it": "↩️ Indietro", "zh": "↩️ 返回", "ja": "↩️ 戻る",
    },
    "language": {
        "ar": "🌐 اللغة", "en": "🌐 Language", "fr": "🌐 Langue",
        "es": "🌐 Idioma", "de": "🌐 Sprache", "ru": "🌐 Язык",
        "tr": "🌐 Dil", "hi": "🌐 भाषा", "pt": "🌐 Idioma",
        "it": "🌐 Lingua", "zh": "🌐 语言", "ja": "🌐 言語",
    },
    "vip": {
        "ar": "👑 لوحة VIP", "en": "👑 VIP Panel", "fr": "👑 Panneau VIP",
        "es": "👑 Panel VIP", "de": "👑 VIP-Panel", "ru": "👑 VIP-Панель",
        "tr": "👑 VIP Paneli", "hi": "👑 VIP पैनल", "pt": "👑 Painel VIP",
        "it": "👑 Pannello VIP", "zh": "👑 VIP 面板", "ja": "👑 VIPパネル",
    },
    "charge": {
        "ar": "💳 شحن رصيد", "en": "💳 Charge Balance", "fr": "💳 Recharger",
        "es": "💳 Recargar", "de": "💳 Aufladen", "ru": "💳 Пополнить",
        "tr": "💳 Bakiye Yükle", "hi": "💳 रिचार्ज", "pt": "💳 Recarregar",
        "it": "💳 Ricarica", "zh": "💳 充值", "ja": "💳 チャージ",
    },
    "updates": {
        "ar": "📅 التحديثات القادمة", "en": "📅 Upcoming Updates", "fr": "📅 Mises à Jour",
        "es": "📅 Próximas Act.", "de": "📅 Kommende Updates", "ru": "📅 Будущие Обновления",
        "tr": "📅 Yaklaşan Güncellemeler", "hi": "📅 आगामी अपडेट", "pt": "📅 Próximas Atualizações",
        "it": "📅 Prossimi Aggiornamenti", "zh": "📅 即将更新", "ja": "📅 次回アップデート",
    },
    "tasks": {
        "ar": "🎯 مهام يومية", "en": "🎯 Daily Tasks", "fr": "🎯 Tâches Quotidiennes",
        "es": "🎯 Tareas Diarias", "de": "🎯 Tägliche Aufgaben", "ru": "🎯 Ежедневные Задачи",
        "tr": "🎯 Günlük Görevler", "hi": "🎯 दैनिक कार्य", "pt": "🎯 Tarefas Diárias",
        "it": "🎯 Attività Giornaliere", "zh": "🎯 每日任务", "ja": "🎯 デイリータスク",
    },
    "achievements": {
        "ar": "🏅 إنجازاتي", "en": "🏅 Achievements", "fr": "🏅 Réalisations",
        "es": "🏅 Logros", "de": "🏅 Erfolge", "ru": "🏅 Достижения",
        "tr": "🏅 Başarımlar", "hi": "🏅 उपलब्धियाँ", "pt": "🏅 Conquistas",
        "it": "🏅 Obiettivi", "zh": "🏅 成就", "ja": "🏅 実績",
    },
    "history": {
        "ar": "📅 سجل معاملاتي", "en": "📅 Transactions", "fr": "📅 Transactions",
        "es": "📅 Transacciones", "de": "📅 Transaktionen", "ru": "📅 Транзакции",
        "tr": "📅 İşlemlerim", "hi": "📅 लेनदेन", "pt": "📅 Transações",
        "it": "📅 Transazioni", "zh": "📅 交易记录", "ja": "📅 取引履歴",
    },
    "weekly": {
        "ar": "📊 تقريري الأسبوعي", "en": "📊 Weekly Report", "fr": "📊 Rapport Hebdo",
        "es": "📊 Reporte Semanal", "de": "📊 Wochenbericht", "ru": "📊 Недельный Отчёт",
        "tr": "📊 Haftalık Rapor", "hi": "📊 साप्ताहिक रिपोर्ट", "pt": "📊 Relatório Semanal",
        "it": "📊 Report Settimanale", "zh": "📊 周报", "ja": "📊 週次レポート",
    },
    "feedback": {
        "ar": "✉️ اقتراح/شكوى", "en": "✉️ Feedback", "fr": "✉️ Suggestions",
        "es": "✉️ Sugerencias", "de": "✉️ Feedback", "ru": "✉️ Обратная Связь",
        "tr": "✉️ Geri Bildirim", "hi": "✉️ प्रतिक्रिया", "pt": "✉️ Feedback",
        "it": "✉️ Feedback", "zh": "✉️ 反馈", "ja": "✉️ フィードバック",
    },
    "assistant_tools": {
        "ar": "🛠️ أدوات المساعد", "en": "🛠️ AI Tools", "fr": "🛠️ Outils IA",
        "es": "🛠️ Herramientas IA", "de": "🛠️ KI-Tools", "ru": "🛠️ AI-Инструменты",
        "tr": "🛠️ AI Araçları", "hi": "🛠️ AI टूल्स", "pt": "🛠️ Ferramentas IA",
        "it": "🛠️ Strumenti IA", "zh": "🛠️ AI工具", "ja": "🛠️ AIツール",
    },
}

# ═══════════════════════════════════════════════════════════
# الإنجازات (15)
# ═══════════════════════════════════════════════════════════
ACHIEVEMENTS = {
    "first_session": {"name": "🔌 أول جلسة", "reward": 20},
    "first_scrape": {"name": "🕷️ أول سحب", "reward": 20},
    "first_pump": {"name": "🚀 أول ضخ", "reward": 20},
    "scraped_100": {"name": "💯 100 عضو", "reward": 50},
    "scraped_1000": {"name": "🏆 1000 عضو", "reward": 200},
    "scraped_5000": {"name": "👑 5000 عضو", "reward": 500},
    "pumped_10": {"name": "🎯 10 ضخات", "reward": 30},
    "pumped_100": {"name": "🔥 100 ضخة", "reward": 150},
    "streak_7": {"name": "🔥 7 أيام", "reward": 50},
    "streak_30": {"name": "💎 30 يوم", "reward": 300},
    "refs_5": {"name": "👥 5 إحالات", "reward": 50},
    "refs_10": {"name": "🌟 10 إحالات", "reward": 150},
    "points_1000": {"name": "💰 1000 نقطة", "reward": 100},
    "points_10000": {"name": "💎 10000 نقطة", "reward": 500},
    "first_vip": {"name": "👑 أول VIP", "reward": 100},
}

# ═══════════════════════════════════════════════════════════
# المهام اليومية (5)
# ═══════════════════════════════════════════════════════════
DAILY_QUESTS = {
    "q_scrape": {"name": "🕷️ اسحب من جروب", "reward": 10},
    "q_pump": {"name": "🚀 اضخ عضو", "reward": 5},
    "q_gift": {"name": "🎁 استلم هدية", "reward": 3},
    "q_ai": {"name": "🤖 كلم المساعد", "reward": 5},
    "q_wheel": {"name": "🎰 العب العجلة", "reward": 3},
}

# ═══════════════════════════════════════════════════════════
# ثيمات الموقع (8)
# ═══════════════════════════════════════════════════════════
WEB_THEMES = {
    "dark": {
        "name": "🌑 داكن", "bg": "#0b0f19", "bg2": "#1a1f3a",
        "card": "rgba(30, 41, 59, 0.6)", "border": "rgba(255,255,255,0.08)",
        "text": "#f3f4f6", "accent": "#3b82f6", "accent2": "#8b5cf6",
    },
    "ocean": {
        "name": "🌊 محيط", "bg": "#0a1929", "bg2": "#0d2137",
        "card": "rgba(19, 47, 76, 0.6)", "border": "rgba(2, 136, 209, 0.2)",
        "text": "#e0f7fa", "accent": "#0288d1", "accent2": "#00bcd4",
    },
    "sunset": {
        "name": "🌅 غروب", "bg": "#1a0f0a", "bg2": "#2d1810",
        "card": "rgba(45, 24, 16, 0.6)", "border": "rgba(255, 107, 53, 0.2)",
        "text": "#fff3e0", "accent": "#ff6b35", "accent2": "#f7931e",
    },
    "forest": {
        "name": "🌲 غابة", "bg": "#0a1f0a", "bg2": "#0f2e0f",
        "card": "rgba(26, 61, 26, 0.6)", "border": "rgba(76, 175, 80, 0.2)",
        "text": "#e8f5e9", "accent": "#4caf50", "accent2": "#8bc34a",
    },
    "royal": {
        "name": "👑 ملكي", "bg": "#1a0a2e", "bg2": "#2d1b4e",
        "card": "rgba(45, 27, 78, 0.6)", "border": "rgba(156, 39, 176, 0.2)",
        "text": "#f3e5f5", "accent": "#9c27b0", "accent2": "#e91e63",
    },
    "neon": {
        "name": "⚡ نيون", "bg": "#000000", "bg2": "#0a0a1a",
        "card": "rgba(20, 20, 40, 0.7)", "border": "rgba(0, 255, 136, 0.3)",
        "text": "#e0ffe0", "accent": "#00ff88", "accent2": "#ff0088",
    },
    "candy": {
        "name": "🍭 كاندي", "bg": "#1f0a1a", "bg2": "#2d0f2a",
        "card": "rgba(45, 15, 42, 0.6)", "border": "rgba(255, 20, 147, 0.2)",
        "text": "#ffe4f3", "accent": "#ff1493", "accent2": "#ff69b4",
    },
    "cyber": {
        "name": "🤖 سايبر", "bg": "#0a0a0a", "bg2": "#0a1420",
        "card": "rgba(10, 20, 32, 0.7)", "border": "rgba(0, 255, 255, 0.2)",
        "text": "#c8f7ff", "accent": "#00ffff", "accent2": "#ff00ff",
    },
}

# ═══════════════════════════════════════════════════════════
# أسئلة الكويز (15)
# ═══════════════════════════════════════════════════════════
TRIVIA_QUESTIONS = [
    {"q": "ما هي عاصمة مصر؟", "opts": ["الإسكندرية", "القاهرة", "أسوان", "الأقصر"], "ans": 1},
    {"q": "كم عدد أيام السنة الميلادية؟", "opts": ["360", "365", "366", "355"], "ans": 1},
    {"q": "من هو مخترع المصباح الكهربائي؟", "opts": ["نيوتن", "أينشتاين", "إديسون", "أرخميدس"], "ans": 2},
    {"q": "ما هو أطول نهر في العالم؟", "opts": ["النيل", "الأمازون", "المسيسيبي", "اليانغتسي"], "ans": 0},
    {"q": "كم عدد قارات العالم؟", "opts": ["5", "6", "7", "8"], "ans": 2},
    {"q": "من كتب رواية (الحرب والسلام)؟", "opts": ["ديستوفسكي", "تولستوي", "شكسبير", "هيمنغواي"], "ans": 1},
    {"q": "ما هو أكبر كوكب في المجموعة الشمسية؟", "opts": ["المريخ", "زحل", "المشتري", "الأرض"], "ans": 2},
    {"q": "في أي عام نزل الإنسان على القمر؟", "opts": ["1965", "1969", "1972", "1960"], "ans": 1},
    {"q": "ما هي عاصمة اليابان؟", "opts": ["طوكيو", "بكين", "سيول", "أوساكا"], "ans": 0},
    {"q": "كم عدد أضلاع المثلث؟", "opts": ["4", "5", "3", "6"], "ans": 2},
    {"q": "من هو مكتشف الجاذبية؟", "opts": ["إديسون", "نيوتن", "أرخميدس", "أينشتاين"], "ans": 1},
    {"q": "أطول سورة في القرآن؟", "opts": ["البقرة", "آل عمران", "النساء", "المائدة"], "ans": 0},
    {"q": "ما هو الحمض الذي يوجد في الليمون؟", "opts": ["حمض الخليك", "حمض الستريك", "حمض الكبريتيك", "حمض النيتريك"], "ans": 1},
    {"q": "من فاز بكأس العالم 2022؟", "opts": ["فرنسا", "البرازيل", "الأرجنتين", "ألمانيا"], "ans": 2},
    {"q": "ما هو أكبر محيط في العالم؟", "opts": ["الأطلسي", "الهندي", "الهادئ", "المتجمد الشمالي"], "ans": 2},
]

# ═══════════════════════════════════════════════════════════
# التصنيف (8 أنواع)
# ═══════════════════════════════════════════════════════════
FEEDBACK_TYPES = {
    "suggestion": "💡 اقتراح",
    "bug": "🐛 بلاغ باج",
    "complaint": "😠 شكوى",
}

# ═══════════════════════════════════════════════════════════
# إيموجيات موحدة
# ═══════════════════════════════════════════════════════════
E = {
    "spider": "🕷️", "rocket": "🚀", "crown": "👑", "star": "⭐",
    "gift": "🎁", "wheel": "🎡", "trophy": "🏆", "check": "✅",
    "cross": "❌", "warn": "⚠️", "lock": "🔒", "gear": "⚙️",
    "help": "ℹ️", "user": "👤", "money": "💰", "chart": "📊",
}

# ═══════════════════════════════════════════════════════════
# دوال مساعدة
# ═══════════════════════════════════════════════════════════
def get_lang_key(text: str) -> str:
    """يرجع مفتاح الترجمة من نص مترجم"""
    for key, translations in TRANS.items():
        for lang_text in translations.values():
            if text.strip() == lang_text.strip():
                return key
    return None

def t(lang: str, key: str) -> str:
    """يرجع الترجمة حسب اللغة"""
    if key in TRANS:
        return TRANS[key].get(lang, TRANS[key].get("ar", key))
    return key
