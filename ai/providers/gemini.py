"""Gemini Provider"""
import httpx
from ai.providers.base import BaseProvider
from logger import get_logger

log = get_logger("ai.gemini")

class GeminiProvider(BaseProvider):
    NAME = "gemini"
    URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    MODEL = "gemini-2.5-flash"

    async def chat(self, messages, max_tokens=2000, model=None, tools=None):
        if not self.is_available():
            return self._err("Gemini API key missing")
        try:
            async with httpx.AsyncClient(timeout=40) as c:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                payload = {"model": model or self.MODEL, "messages": messages, "max_tokens": max_tokens}
                if tools: payload["tools"] = tools
                r = await c.post(self.URL, headers=headers, json=payload)
                if r.status_code == 200:
                    d = r.json()
                    content = d["choices"][0]["message"].get("content") or ""
                    return self._msg(content)
            return self._err(f"Gemini HTTP {r.status_code}")
        except Exception as e:
            return self._err(str(e)[:100])
