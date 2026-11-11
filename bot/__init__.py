"""Bot package — Python 3.14 event loop fix for Pyrogram"""
import asyncio

# Fix: Python 3.12+ removed auto event loop creation
# Pyrogram 2.0.106 expects a loop at import time
try:
    asyncio.get_running_loop()
except RuntimeError:
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
