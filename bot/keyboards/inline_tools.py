"""Inline Keyboards — أدوات AI التفاعلية للمستخدم"""
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def _ikb(rows: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(rows)


# ═══════════════════════════════════════════════════════════
# 🌤️ Weather
# ═══════════════════════════════════════════════════════════
def weather_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("القاهرة", callback_data="ui_wthr_Cairo"),
         InlineKeyboardButton("الإسكندرية", callback_data="ui_wthr_Alexandria")],
        [InlineKeyboardButton("الرياض", callback_data="ui_wthr_Riyadh"),
         InlineKeyboardButton("دبي", callback_data="ui_wthr_Dubai")],
        [InlineKeyboardButton("لندن", callback_data="ui_wthr_London"),
         InlineKeyboardButton("نيويورك", callback_data="ui_wthr_NewYork")],
    ])


# ═══════════════════════════════════════════════════════════
# 🕌 Prayer times
# ═══════════════════════════════════════════════════════════
def prayer_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("القاهرة", callback_data="ui_pr_القاهرة_مصر"),
         InlineKeyboardButton("الإسكندرية", callback_data="ui_pr_الإسكندرية_مصر")],
        [InlineKeyboardButton("الرياض", callback_data="ui_pr_الرياض_السعودية"),
         InlineKeyboardButton("دبي", callback_data="ui_pr_دبي_الامارات")],
        [InlineKeyboardButton("عمان", callback_data="ui_pr_عمان_الاردن"),
         InlineKeyboardButton("بغداد", callback_data="ui_pr_بغداد_العراق")],
    ])


# ═══════════════════════════════════════════════════════════
# 💰 Crypto
# ═══════════════════════════════════════════════════════════
def crypto_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("Bitcoin", callback_data="ui_cryp_bitcoin"),
         InlineKeyboardButton("Ethereum", callback_data="ui_cryp_ethereum")],
        [InlineKeyboardButton("Binance", callback_data="ui_cryp_binancecoin"),
         InlineKeyboardButton("Solana", callback_data="ui_cryp_solana")],
        [InlineKeyboardButton("Ripple", callback_data="ui_cryp_ripple"),
         InlineKeyboardButton("Dogecoin", callback_data="ui_cryp_dogecoin")],
        [InlineKeyboardButton("Cardano", callback_data="ui_cryp_cardano"),
         InlineKeyboardButton("Polkadot", callback_data="ui_cryp_polkadot")],
        [InlineKeyboardButton("Shiba Inu", callback_data="ui_cryp_shiba-inu"),
         InlineKeyboardButton("Litecoin", callback_data="ui_cryp_litecoin")],
    ])


# ═══════════════════════════════════════════════════════════
# 📈 Stocks
# ═══════════════════════════════════════════════════════════
def stock_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("Apple", callback_data="ui_stk_AAPL"),
         InlineKeyboardButton("Microsoft", callback_data="ui_stk_MSFT")],
        [InlineKeyboardButton("Tesla", callback_data="ui_stk_TSLA"),
         InlineKeyboardButton("Google", callback_data="ui_stk_GOOGL")],
        [InlineKeyboardButton("Amazon", callback_data="ui_stk_AMZN"),
         InlineKeyboardButton("Meta", callback_data="ui_stk_META")],
        [InlineKeyboardButton("Nvidia", callback_data="ui_stk_NVDA"),
         InlineKeyboardButton("Netflix", callback_data="ui_stk_NFLX")],
        [InlineKeyboardButton("AMD", callback_data="ui_stk_AMD"),
         InlineKeyboardButton("Intel", callback_data="ui_stk_INTC")],
    ])


# ═══════════════════════════════════════════════════════════
# 💱 Currency conversion
# ═══════════════════════════════════════════════════════════
def currency_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("100$ -> جنيه", callback_data="ui_cur_100_USD_EGP"),
         InlineKeyboardButton("100$ -> ريال", callback_data="ui_cur_100_USD_SAR")],
        [InlineKeyboardButton("100€ -> جنيه", callback_data="ui_cur_100_EUR_EGP"),
         InlineKeyboardButton("1000 جنيه -> $", callback_data="ui_cur_1000_EGP_USD")],
        [InlineKeyboardButton("1000 ريال -> جنيه", callback_data="ui_cur_1000_SAR_EGP"),
         InlineKeyboardButton("100 درهم -> جنيه", callback_data="ui_cur_100_AED_EGP")],
    ])


# ═══════════════════════════════════════════════════════════
# 📏 Units conversion
# ═══════════════════════════════════════════════════════════
def units_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("10 كيلو -> باوند", callback_data="ui_unt_10_kg_lb"),
         InlineKeyboardButton("10 كم -> ميل", callback_data="ui_unt_10_km_miles")],
        [InlineKeyboardButton("100 سم -> بوصة", callback_data="ui_unt_100_cm_inch"),
         InlineKeyboardButton("50 ميل -> كم", callback_data="ui_unt_50_miles_km")],
        [InlineKeyboardButton("1 متر -> قدم", callback_data="ui_unt_1_m_ft"),
         InlineKeyboardButton("100 باوند -> كيلو", callback_data="ui_unt_100_lb_kg")],
    ])


# ═══════════════════════════════════════════════════════════
# 🎯 Quiz
# ═══════════════════════════════════════════════════════════
def quiz_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("🔬 علوم", callback_data="ui_quiz_علوم"),
         InlineKeyboardButton("📜 تاريخ", callback_data="ui_quiz_تاريخ")],
        [InlineKeyboardButton("⚽ رياضة", callback_data="ui_quiz_رياضة"),
         InlineKeyboardButton("🕌 إسلامي", callback_data="ui_quiz_اسلامي")],
        [InlineKeyboardButton("🎲 عشوائي", callback_data="ui_quiz_عشوائي")],
    ])


# ═══════════════════════════════════════════════════════════
# 🍳 Recipe
# ═══════════════════════════════════════════════════════════
def recipe_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("🍳 فطار", callback_data="ui_rcp_فطار"),
         InlineKeyboardButton("🥩 غدا", callback_data="ui_rcp_غدا")],
        [InlineKeyboardButton("🍰 حلويات", callback_data="ui_rcp_حلويات"),
         InlineKeyboardButton("🥗 صحي", callback_data="ui_rcp_صحي")],
    ])


# ═══════════════════════════════════════════════════════════
# 📰 Anime
# ═══════════════════════════════════════════════════════════
def anime_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("⚔️ أكشن", callback_data="ui_anm_اكشن"),
         InlineKeyboardButton("💖 رومانسي", callback_data="ui_anm_رومانسي")],
        [InlineKeyboardButton("😂 كوميدي", callback_data="ui_anm_كوميدي"),
         InlineKeyboardButton("🏆 الأعلى تقييماً", callback_data="ui_anm_الأعلى_تقييماً")],
    ])


# ═══════════════════════════════════════════════════════════
# 📊 Chart
# ═══════════════════════════════════════════════════════════
def chart_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("👥 إحصائيات المستخدمين", callback_data="ui_cht_users")],
        [InlineKeyboardButton("📈 إحصائيات السحب والضخ", callback_data="ui_cht_stats")],
        [InlineKeyboardButton("💰 أفضل 5 مستخدمين", callback_data="ui_cht_top")],
        [InlineKeyboardButton("✏️ رسم مخصص (فويس/نص)", callback_data="ui_cht_custom")],
    ])


# ═══════════════════════════════════════════════════════════
# 🧮 Calculator (grid 4×5)
# ═══════════════════════════════════════════════════════════
def calculator_keyboard() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("7", callback_data="calc_7"),
         InlineKeyboardButton("8", callback_data="calc_8"),
         InlineKeyboardButton("9", callback_data="calc_9"),
         InlineKeyboardButton("÷", callback_data="calc_/")],
        [InlineKeyboardButton("4", callback_data="calc_4"),
         InlineKeyboardButton("5", callback_data="calc_5"),
         InlineKeyboardButton("6", callback_data="calc_6"),
         InlineKeyboardButton("×", callback_data="calc_*")],
        [InlineKeyboardButton("1", callback_data="calc_1"),
         InlineKeyboardButton("2", callback_data="calc_2"),
         InlineKeyboardButton("3", callback_data="calc_3"),
         InlineKeyboardButton("-", callback_data="calc_-")],
        [InlineKeyboardButton("0", callback_data="calc_0"),
         InlineKeyboardButton(".", callback_data="calc_."),
         InlineKeyboardButton("=", callback_data="calc_="),
         InlineKeyboardButton("+", callback_data="calc_+")],
        [InlineKeyboardButton("C", callback_data="calc_C"),
         InlineKeyboardButton("⌫", callback_data="calc_B")],
    ])


# ═══════════════════════════════════════════════════════════
# 🎯 More Tools (الأدوات الإضافية)
# ═══════════════════════════════════════════════════════════
def more_tools_menu() -> InlineKeyboardMarkup:
    return _ikb([
        [InlineKeyboardButton("💰 كريبتو", callback_data="ai_x_crypto"),
         InlineKeyboardButton("📈 أسهم", callback_data="ai_x_stock"),
         InlineKeyboardButton("🌤️ الطقس", callback_data="ai_x_weather")],
        [InlineKeyboardButton("🕌 الصلاة", callback_data="ai_x_prayer"),
         InlineKeyboardButton("🧮 حاسبة", callback_data="ai_x_calc"),
         InlineKeyboardButton("💱 عملات", callback_data="ai_x_currency"),
         InlineKeyboardButton("📏 وحدات", callback_data="ai_x_units")],
        [InlineKeyboardButton("🔐 كلمة سر", callback_data="ai_x_password"),
         InlineKeyboardButton("🔗 اختصار URL", callback_data="ai_x_shorten")],
        [InlineKeyboardButton("🌐 فحص IP", callback_data="ai_x_ip"),
         InlineKeyboardButton("🕵️ هوية وهمية", callback_data="ai_x_identity")],
        [InlineKeyboardButton("📖 قاموس", callback_data="ai_x_dict"),
         InlineKeyboardButton("📚 كتب", callback_data="ai_x_books"),
         InlineKeyboardButton("📰 أنمي", callback_data="ai_x_anime")],
        [InlineKeyboardButton("🍳 وصفات", callback_data="ai_x_recipe"),
         InlineKeyboardButton("🏥 طبي", callback_data="ai_x_medical")],
        [InlineKeyboardButton("🧩 ألغاز", callback_data="ai_x_riddle"),
         InlineKeyboardButton("💡 حقائق", callback_data="ai_x_fact"),
         InlineKeyboardButton("🎯 كويز", callback_data="ai_x_quiz")],
        [InlineKeyboardButton("📱 QR", callback_data="ai_x_qr"),
         InlineKeyboardButton("📸 سكرين شوت", callback_data="ai_x_shot")],
        [InlineKeyboardButton("✨ نصوص مزخرفة", callback_data="ai_x_fancy")],
        [InlineKeyboardButton("📋 مهامي", callback_data="ai_x_todos"),
         InlineKeyboardButton("📝 ملاحظاتي", callback_data="ai_x_notes")],
    ])
