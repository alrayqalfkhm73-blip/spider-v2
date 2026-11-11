"""Mock Telegram API — للاختبار offline"""
from typing import AsyncIterator
from bot.testing import MockUser, MockChat, MockMessage

class MockMember:
    def __init__(self, user):
        self.user = user

class MockTGClient:
    """يحاكي Pyrogram Client"""

    def __init__(self, members_count=20, history_count=10):
        self.members_count = members_count
        self.history_count = history_count
        self.added = []
        self.added_lock = False

    async def get_chat_members(self, chat_id):
        for i in range(self.members_count):
            if i % 3 == 0:
                # bot — should be filtered
                u = MockUser(1000 + i, f"Bot{i}", None)
                u.is_bot = True
            elif i % 5 == 0:
                # no username — filtered by username_only
                u = MockUser(2000 + i, f"NoUser{i}", None)
                u.is_bot = False
            else:
                u = MockUser(3000 + i, f"User{i}", f"user{i}")
                u.is_bot = False
            yield MockMember(u)

    async def get_chat_history(self, chat_id, limit=100):
        for i in range(min(self.history_count, limit)):
            u = MockUser(5000 + i, f"Hist{i}", f"hist{i}")
            msg = MockMessage(f"message {i}", u.id, u.first_name, u.username)
            yield msg

    async def add_chat_members(self, chat_id, user_id):
        if self.added_lock:
            raise Exception("PEER_FLOOD")
        self.added.append(user_id)
        return True

    async def get_chat(self, chat_id):
        return MockChat(chat_id, "Mock Chat")
