"""Providers registry"""
from config import config
from ai.providers.groq import GroqProvider
from ai.providers.nvidia import NVIDIAProvider
from ai.providers.openrouter import OpenRouterProvider
from ai.providers.gemini import GeminiProvider
from ai.providers.pollinations import PollinationsProvider

def get_providers():
    """يرجع قائمة الـ providers المتاحة"""
    return {
        "groq": GroqProvider(config.ai.groq),
        "nvidia": NVIDIAProvider(config.ai.nvidia),
        "openrouter": OpenRouterProvider(config.ai.openrouter),
        "gemini": GeminiProvider(config.ai.gemini),
        "pollinations": PollinationsProvider(),
    }
