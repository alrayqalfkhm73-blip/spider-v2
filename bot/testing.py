"""Mock Pyrogram objects for testing"""
from datetime import datetime

class MockUser:
    def __init__(self, uid=123456, first_name="Test", username="testuser"):
        self.id = uid
        self.first_name = first_name
        self.username = username

class MockChat:
    def __init__(self, cid=123456, title="Test Chat"):
        self.id = cid
        self.title = title
        self.type = "private"

class MockMessage:
    def __init__(self, text="", user_id=123456, first_name="Test", username="testuser"):
        self.text = text
        self.from_user = MockUser(user_id, first_name, username)
        self.chat = MockChat(user_id)
        self.replies = []
        self.photos = []
        self.documents = []
        self.command = text.split()[0][1:] if text.startswith("/") else None

    async def reply_text(self, text, reply_markup=None, **kwargs):
        self.replies.append(text)
        return self

    async def reply_photo(self, photo, caption="", **kwargs):
        self.photos.append({"photo": photo, "caption": caption})
        return self

    async def reply_document(self, document, caption="", **kwargs):
        self.documents.append({"doc": document, "caption": caption})
        return self

    async def delete(self):
        pass

class MockClient:
    def __init__(self):
        self.messages_sent = []
        self.me = MockUser(999, "Bot", "spider_test_bot")

    async def send_message(self, chat_id, text, **kwargs):
        self.messages_sent.append({"chat_id": chat_id, "text": text})
        return MockMessage(text)

    async def get_me(self):
        return self.me

    async def start(self):
        pass

    async def stop(self):
        pass
