"""Base Provider — abstract interface"""
from logger import get_logger

log = get_logger("ai.base")

class BaseProvider:
    NAME = "base"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: list, max_tokens: int = 2000,
                   model: str = None, tools: list = None) -> dict:
        raise NotImplementedError

    def _msg(self, content: str) -> dict:
        return {"role": "assistant", "content": content, "tool_calls": None}

    def _err(self, error: str) -> dict:
        return {"error": error, "content": None, "tool_calls": None}
