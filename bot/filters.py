"""Custom Pyrogram filters"""
from pyrogram import filters
from config import config

is_owner = filters.user(config.telegram.owner_id)

def is_owner_id(user_id: int) -> bool:
    return user_id == config.telegram.owner_id
