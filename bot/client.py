"""Pyrogram Client — Lazy init with plugins"""
import asyncio
from config import config
from logger import get_logger

log = get_logger("bot.client")
_client = None

def _ensure_loop():
    """يضمن وجود event loop قبل Pyrogram"""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        try:
            asyncio.get_event_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())


def get_bot():
    """يرجع الـ client (lazy init)"""
    global _client
    if _client is None:
        _ensure_loop()
        from pyrogram import Client
        _client = Client(
            "spider_v2_session",
            api_id=config.telegram.api_id,
            api_hash=config.telegram.api_hash,
            bot_token=config.telegram.bot_token,
            device_model="Samsung SM-S918B",
            system_version="SDK 34",
            app_version="10.6.1",
            lang_code="ar",
            plugins={"root": "bot.handlers"},  # ← مهم جداً — بيحمل handlers
        )
        log.info("Client created (lazy)")
    return _client


def is_ready() -> bool:
    """هل البوت شغال؟"""
    try:
        return _client is not None and _client.is_connected
    except Exception:
        return False


async def start_bot():
    """يبدأ البوت"""
    client = get_bot()
    try:
        await client.start()
        me = await client.get_me()
        log.info(f"Bot started: @{me.username}")
        
        # ═══ DIAGNOSTIC: اطبع عدد الـ handlers المسجلين ═══
        try:
            await asyncio.sleep(1)  # ندي وقت للـ plugins يتحملوا
            total = 0
            for group_id, handlers_list in client.dispatcher.groups.items():
                for h in handlers_list:
                    total += 1
            log.info(f"[DIAG] Total registered handlers: {total}")
        except Exception as e:
            log.warning(f"[DIAG] {e}")
        
        return True
    except Exception as e:
        log.error(f"Bot start failed: {e}")
        return False


async def stop_bot():
    global _client
    if _client:
        try:
            await _client.stop()
            log.info("Bot stopped")
        except Exception:
            pass
        _client = None
