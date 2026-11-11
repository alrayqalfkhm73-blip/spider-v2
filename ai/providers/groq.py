"""Groq Provider"""
import asyncio
from ai.providers.base import BaseProvider
from logger import get_logger

log = get_logger("ai.groq")

class GroqProvider(BaseProvider):
    NAME = "groq"
    MODELS = ["openai/gpt-oss-20b", "qwen/qwen3.8-27b", "openai/gpt-oss-120b"]

    async def chat(self, messages, max_tokens=2000, model=None, tools=None):
        if not self.is_available():
            return self._err("Groq API key missing")
        try:
            import groq
            client = groq.Groq(api_key=self.api_key)
            models = [model] if model else self.MODELS
            for m in models:
                try:
                    def _call():
                        kw = {"model": m, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}
                        if tools: kw["tools"] = tools
                        return client.chat.completions.create(**kw)
                    r = await asyncio.wait_for(asyncio.to_thread(_call), timeout=30)
                    msg = r.choices[0].message
                    return self._msg(msg.content or "")
                except Exception as e:
                    log.warning(f"Groq {m} failed: {str(e)[:60]}")
                    continue
            return self._err("All Groq models failed")
        except ImportError:
            return self._err("groq package missing")
        except Exception as e:
            return self._err(str(e)[:100])
