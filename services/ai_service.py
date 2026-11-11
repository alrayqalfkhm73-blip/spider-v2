"""AI Service — MoA على 8091"""
import asyncio
from flask import Flask, request, jsonify
from config import config
from ai.providers import get_providers
from logger import get_logger

log = get_logger("ai.service")

app = Flask(__name__)

def _moa_chain():
    providers = get_providers()
    return [
        ("groq", providers["groq"], "openai/gpt-oss-120b"),
        ("nvidia", providers["nvidia"], "nvidia/nemotron-3-ultra-550b-a55b"),
        ("openrouter", providers["openrouter"], None),
        ("gemini", providers["gemini"], None),
        ("pollinations", providers["pollinations"], None),
    ]

async def run_moa(messages: list, max_tokens: int = 4000, user_id: str = "default") -> dict:
    """MoA مصغر: 2 موديلات parallel + synth + fallback"""
    providers = get_providers()
    meta = {"pipeline": "moa", "drafts": 0, "provider": None, "models_used": []}

    # ═══ Phase 1: 2 drafts parallel ═══
    drafters = [
        ("groq", providers["groq"], "openai/gpt-oss-120b"),
        ("gemini", providers["gemini"], None),
    ]
    tasks = []
    for name, p, model in drafters:
        if p.is_available():
            tasks.append((name, asyncio.create_task(p.chat(messages, max_tokens, model))))

    drafts = []
    for name, t in tasks:
        try:
            r = await asyncio.wait_for(t, timeout=45)
            if r.get("content"):
                drafts.append({"provider": name, "content": r["content"]})
                meta["models_used"].append(name)
        except Exception as e:
            log.debug(f"Draft {name} failed: {str(e)[:60]}")

    meta["drafts"] = len(drafts)

    # ═══ Phase 2: Sythesize if 2+ drafts ═══
    if len(drafts) >= 2:
        synth_msg = [
            {"role": "system", "content": "ادمج أفضل الأفكار من هذه المسودات في إجابة واحدة واضحة بالعربي. لا تذكر أنك تدمج."},
            {"role": "user", "content": f"السؤال: {messages[-1].get('content','')}\n\n" +
                "\n\n".join([f"مسودة {i+1}:\n{d['content'][:1500]}" for i, d in enumerate(drafts)])}
        ]
        try:
            synth = await providers["groq"].chat(synth_msg, max_tokens, "openai/gpt-oss-120b")
            if synth.get("content"):
                meta["pipeline"] = "moa_full"
                meta["provider"] = "moa_synth"
                return {"content": synth["content"], "meta": meta}
        except: pass

    # ═══ Phase 3: Use best draft ═══
    if drafts:
        meta["provider"] = drafts[0]["provider"]
        meta["pipeline"] = "moa_best_draft"
        return {"content": drafts[0]["content"], "meta": meta}

    # ═══ Phase 4: Pollinations fallback ═══
    try:
        r = await providers["pollinations"].chat(messages, max_tokens)
        if r.get("content"):
            meta["provider"] = "pollinations"
            meta["pipeline"] = "fallback"
            return {"content": r["content"], "meta": meta}
    except: pass

    return {"content": None, "error": "all providers failed", "meta": meta}

@app.route("/health", methods=["GET"])
def health():
    providers = get_providers()
    total_models = 3 + 3 + 3 + 1 + 1  # groq + nvidia + or + gemini + pollinations
    return jsonify({
        "status": "ok",
        "pipeline": "MoA",
        "total_models": total_models,
        "available": {name: p.is_available() for name, p in providers.items()},
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    messages = data.get("messages", [])
    max_tokens = data.get("max_tokens", 4000)
    user_id = str(data.get("user_id", "default"))

    if not messages:
        return jsonify({"error": "messages required"}), 400

    try:
        result = asyncio.run(run_moa(messages, max_tokens, user_id))
        log.info(f"MoA: pipeline={result.get('meta',{}).get('pipeline')} provider={result.get('meta',{}).get('provider')}")
        return jsonify(result)
    except Exception as e:
        log.error(f"MoA failed: {e}")
        return jsonify({"error": str(e)[:100]}), 500

def run_ai_service():
    log.info(f"AI Service starting on port {config.web.ai_port}")
    app.run(host="127.0.0.1", port=config.web.ai_port, threaded=True)
