"""Middleware — الحماية"""
from functools import wraps
from database.queries import users
from bot.texts import fmt
from logger import get_logger

log = get_logger("bot.middleware")

MAINTENANCE = {"active": False}

def set_maintenance(active: bool):
    MAINTENANCE["active"] = active

def is_maintenance() -> bool:
    return MAINTENANCE["active"]

def ban_check(func):
    """يمنع المحظورين"""
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        uid = message.from_user.id
        if users.is_banned(uid):
            try:
                await message.reply_text(fmt("banned"))
            except: pass
            return
        return await func(client, message, *args, **kwargs)
    return wrapper

def maintenance_check(func):
    """يمنع غير المالك وقت الصيانة"""
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        from config import config
        uid = message.from_user.id
        if is_maintenance() and uid != config.telegram.owner_id:
            try:
                await message.reply_text(fmt("maintenance"))
            except: pass
            return
        return await func(client, message, *args, **kwargs)
    return wrapper

def owner_only(func):
    """للمالك فقط"""
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        from config import config
        if message.from_user.id != config.telegram.owner_id:
            try:
                await message.reply_text(fmt("admin_only"))
            except: pass
            return
        return await func(client, message, *args, **kwargs)
    return wrapper
