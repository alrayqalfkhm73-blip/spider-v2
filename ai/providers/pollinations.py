"""Pollinations — مجاني تماماً بدون مفتاح"""
import httpx
from ai.providers.base import BaseProvider
from logger import get_logger

log = get_logger("ai.poll")

class PollinationsProvider(BaseProvider):
    NAME = "pollinations"
    URL = "https://text.pollinations.ai/openai"

    def is_available(self) -> bool:
        return True  # مفيش key

    async def chat(self, messages, max_tokens=2000, model=None, tools=None):
        try:
            async with httpx.AsyncClient(timeout=60) as c:
                payload = {"model": "openai", "messages": messages, "max_tokens": max_tokens}
                r = await c.post(self.URL, json=payload)
                if r.status_code == 200:
                    d = r.json()
                    content = d["choices"][0]["message"].get("content") or ""
                    return self._msg(content)
            return self._err(f"Pollinations HTTP {r.status_code}")
        except Exception as e:
            return self._err(str(e)[:100])
