"""Handlers package"""
import asyncio
try: asyncio.get_running_loop()
except RuntimeError:
    try: asyncio.get_event_loop()
    except RuntimeError: asyncio.set_event_loop(asyncio.new_event_loop())

from bot.handlers import start, menu, help, admin, scrape, pump, ai_chat, ping
