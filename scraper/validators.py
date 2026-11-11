"""Validators — فلترة الأعضاء"""
from logger import get_logger

log = get_logger("scraper.validators")

# Filter presets
PRESETS = {
    "all": {"usernames_only": False, "active_only": False},
    "usernames_only": {"usernames_only": True, "active_only": False},
    "active_only": {"usernames_only": False, "active_only": True},
    "usernames_active": {"usernames_only": True, "active_only": True},
    "with_photo": {"usernames_only": False, "active_only": False, "with_photo": True},
}

def should_scrape(user, filters: dict = None) -> dict:
    """يرجع {ok: bool, reason: str}"""
    if user is None:
        return {"ok": False, "reason": "no_user"}

    # Basic filters
    if getattr(user, "is_bot", False):
        return {"ok": False, "reason": "bot"}
    if getattr(user, "is_deleted", False):
        return {"ok": False, "reason": "deleted"}
    if getattr(user, "is_scam", False):
        return {"ok": False, "reason": "scam"}
    if getattr(user, "is_fake", False):
        return {"ok": False, "reason": "fake"}

    filters = filters or {}

    # Username only (المطلوب)
    if filters.get("usernames_only", False):
        if not getattr(user, "username", None):
            return {"ok": False, "reason": "no_username"}

    # With photo
    if filters.get("with_photo", False):
        photos = getattr(user, "photo", None)
        if not photos:
            return {"ok": False, "reason": "no_photo"}

    return {"ok": True, "reason": "ok"}

def make_member_tuple(user, source: str = "") -> tuple:
    """يحول user → tuple للسحب"""
    uid = str(user.id)
    username = getattr(user, "username", None)
    ident = f"@{username}" if username else uid
    from datetime import datetime
    return (ident, username, uid, source, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def is_blacklisted(member_id: str, owner_id: str) -> bool:
    from database.connection import get_db
    row = get_db().fetchone(
        "SELECT 1 FROM blacklist WHERE id=? AND owner_user_id=?",
        (member_id, str(owner_id))
    )
    return row is not None
