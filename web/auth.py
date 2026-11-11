"""Authentication logic"""
import hashlib
from flask import session
from database.queries import users
from database.connection import get_db
from config import config
from logger import get_logger

log = get_logger("web.auth")
db = get_db()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_login(user_id: str, password: str) -> dict:
    user_id = str(user_id).strip()
    password = (password or "").strip()

    if not user_id or not password:
        return {"ok": False, "error": "ID والباسورد مطلوبين"}

    # Owner
    if user_id == str(config.telegram.owner_id):
        if password == config.web.owner_web_pass:
            log.info(f"Login: OWNER {user_id}")
            return {"ok": True, "is_owner": True, "user_id": user_id}
        log.warning(f"Wrong owner password attempt: {user_id}")
        return {"ok": False, "error": "باسورد المالك غلط"}

    # Regular user
    user = users.get_user(user_id)
    if not user:
        return {"ok": False, "error": "المستخدم مش موجود (ابعت /start للبوت أول)"}

    stored = user.get("web_password")

    # First-time login
    if not stored:
        if len(password) < 4:
            return {"ok": False, "error": "الباسورد قصير (4 حروف على الأقل)"}
        try:
            db.execute("UPDATE users SET web_password=? WHERE id=?",
                       (hash_password(password), user_id), commit=True)
            log.info(f"Set first password for {user_id}")
            return {"ok": True, "is_owner": False, "user_id": user_id}
        except Exception as e:
            log.error(f"Set password failed: {e}")
            return {"ok": False, "error": "خطأ في حفظ الباسورد"}

    # Regular check
    if stored == hash_password(password):
        log.info(f"Login: USER {user_id}")
        return {"ok": True, "is_owner": False, "user_id": user_id}

    log.warning(f"Wrong password: {user_id}")
    return {"ok": False, "error": "باسورد غلط"}

def get_session_user():
    if not session.get("logged_in"):
        return None
    return {
        "user_id": session.get("user_id"),
        "is_owner": bool(session.get("is_owner")),
    }
