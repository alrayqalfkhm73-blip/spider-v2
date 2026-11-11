"""OpenRouter Provider"""
import httpx
from ai.providers.base import BaseProvider
from logger import get_logger

log = get_logger("ai.or")

class OpenRouterProvider(BaseProvider):
    NAME = "openrouter"
    URL = "https://openrouter.ai/api/v1/chat/completions"
    MODELS = [
        "typesafe/jev-router",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "openrouter/free",
    ]

    async def chat(self, messages, max_tokens=2000, model=None, tools=None):
        if not self.is_available():
            return self._err("OpenRouter API key missing")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://spider-bot.app"
        }
        models = [model] if model else self.MODELS
        for m in models:
            try:
                async with httpx.AsyncClient(timeout=40) as c:
                    payload = {"model": m, "messages": messages, "max_tokens": max_tokens}
                    if tools: payload["tools"] = tools
                    r = await c.post(self.URL, headers=headers, json=payload)
                    if r.status_code == 200:
                        d = r.json()
                        content = d["choices"][0]["message"].get("content") or ""
                        return self._msg(content)
            except Exception as e:
                log.warning(f"OR {m[:30]} failed: {str(e)[:60]}")
                continue
        return self._err("All OpenRouter models failed")
