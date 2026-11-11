"""bot.keyboards — كل الأزرار من v1

"""

# Submodules
from bot.keyboards import constants
from bot.keyboards import menus
from bot.keyboards import inline_basic
from bot.keyboards import inline_tools
from bot.keyboards import inline_admin

# Re-export كل دوال الـ menus للـ backward compatibility
from bot.keyboards.menus import (
    user_menu, main_menu, get_start_menu, assistant_keyboard,
    scrape_menu, pump_menu, sessions_menu, proxies_menu,
    users_menu, marketing_menu, system_menu, tools_menu,
    stats_menu, ai_tools_menu,
)

# Re-export كل الثوابت
from bot.keyboards.constants import (
    LANGUAGES, TRANS, ACHIEVEMENTS, DAILY_QUESTS,
    WEB_THEMES, TRIVIA_QUESTIONS, FEEDBACK_TYPES, E,
    t, get_lang_key,
)

__all__ = [
    # Submodules
    "constants", "menus", "inline_basic", "inline_tools", "inline_admin",
    # Menus
    "user_menu", "main_menu", "get_start_menu", "assistant_keyboard",
    "scrape_menu", "pump_menu", "sessions_menu", "proxies_menu",
    "users_menu", "marketing_menu", "system_menu", "tools_menu",
    "stats_menu", "ai_tools_menu",
    # Constants
    "LANGUAGES", "TRANS", "ACHIEVEMENTS", "DAILY_QUESTS",
    "WEB_THEMES", "TRIVIA_QUESTIONS", "FEEDBACK_TYPES", "E",
    "t", "get_lang_key",
]
