"""AI Router — Fallback Chain & Error Handling"""
import httpx
from config import config
from ai.providers import get_providers
from ai.search_engine import search_web
from ai import memory
from ai.prompts import system_prompt
from logger import get_logger
import asyncio

log = get_logger("ai.router")

def _build_messages(message: str, user_id: str, is_owner: bool, mode: str, search_results: str = None) -> list:
    import re
    persona = "default"
    match = re.match(r'^\[Persona:\s*(\w+)\]\s*', message)
    if match:
        persona = match.group(1)
        message = message[match.end():]

    history = memory.load_context(str(user_id), limit=6)
    msgs = [{"role": "system", "content": system_prompt(is_owner, mode, persona)}]
    for h in history:
        msgs.append(h)
    if search_results:
        msgs.append({"role": "system", "content": f"📚 نتائج بحث حقيقية:\n{search_results}\n\nاستخدمها في الرد."})
    msgs.append({"role": "user", "content": message})
    return msgs

async def _fast(message: str, user_id: str, is_owner: bool) -> dict:
    providers = get_providers()
    msgs = _build_messages(message, user_id, is_owner, "fast")
    # ترتيب الأسرع أولاً
    chain = [("groq", providers["groq"]), ("nvidia", providers["nvidia"]), ("pollinations", providers["pollinations"])]
    for name, p in chain:
        if not p.is_available(): continue
        try:
            r = await p.chat(msgs, max_tokens=1500)
            if r.get("content"):
                log.info(f"Fast reply via {name}")
                return {"reply": r["content"], "mode": "fast", "provider": name}
        except Exception as e:
            log.warning(f"Fast {name} failed: {str(e)[:60]}")
    return {"reply": "يا قائد، فيه ضغط على الشبكة دلوقتي. جرب تاني بعد شوية.", "mode": "fast", "error": True}

async def _search(message: str, user_id: str, is_owner: bool) -> dict:
    results = await search_web(message, max_results=5)
    msgs = _build_messages(message, user_id, is_owner, "search", results)
    providers = get_providers()
    chain = [("groq", providers["groq"]), ("gemini", providers["gemini"]), ("pollinations", providers["pollinations"])]
    for name, p in chain:
        if not p.is_available(): continue
        try:
            r = await p.chat(msgs, max_tokens=2000)
            if r.get("content"):
                return {"reply": r["content"], "mode": "search", "provider": name, "search_hit": bool(results)}
        except Exception as e:
            log.warning(f"Search {name} failed: {str(e)[:60]}")
    return {"reply": "البحث مش رجع نتيجة. جرب صياغة تانية.", "mode": "search", "error": True}

async def _think(message: str, user_id: str, is_owner: bool) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"http://127.0.0.1:{config.web.ai_port}/health")
            if r.status_code == 200:
                msgs = _build_messages(message, user_id, is_owner, "think")
                async with httpx.AsyncClient(timeout=120) as c2:
                    resp = await c2.post(f"http://127.0.0.1:{config.web.ai_port}/chat", json={"messages": msgs, "user_id": str(user_id), "max_tokens": 4000})
                    if resp.status_code == 200:
                        d = resp.json()
                        if d.get("content"):
                            return {"reply": d["content"], "mode": "think", "provider": "ai_service"}
    except Exception as e:
        pass

    msgs = _build_messages(message, user_id, is_owner, "think")
    providers = get_providers()
    chain = [("groq", providers["groq"]), ("nvidia", providers["nvidia"]), ("openrouter", providers["openrouter"]), ("pollinations", providers["pollinations"])]
    for name, p in chain:
        if not p.is_available(): continue
        try:
            r = await p.chat(msgs, max_tokens=3000)
            if r.get("content"):
                return {"reply": r["content"], "mode": "think", "provider": name}
        except Exception as e:
            pass
    return {"reply": "التفكير فشل. جرب سؤال أبسط.", "mode": "think", "error": True}

async def ask(message: str, user_id: str, is_owner: bool = False, mode: str = "fast") -> dict:
    message = (message or "").strip()
    if not message:
        return {"reply": "اكتب رسالتك", "error": True}
    memory.save_message(str(user_id), "user", message)
    try:
        if mode == "search": result = await _search(message, user_id, is_owner)
        elif mode == "think": result = await _think(message, user_id, is_owner)
        else: result = await _fast(message, user_id, is_owner)

        if result.get("reply") and not result.get("error"):
            memory.save_message(str(user_id), "assistant", result["reply"])
        return result
    except Exception as e:
        log.error(f"ask failed: {e}")
        return {"reply": "حصل خطأ داخلي، جرب تاني.", "error": True}
