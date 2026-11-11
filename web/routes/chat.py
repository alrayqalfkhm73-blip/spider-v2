"""Chat API + AI Vision + ZIP Analyzer"""
from flask import Blueprint, request, jsonify, session
from web.deps import require_login, get_uid
from ai.router import ask
from logger import get_logger
import asyncio
import httpx
from config import config
import base64
import os
import tempfile
import zipfile
import shutil

bp = Blueprint("chat", __name__)
log = get_logger("web.chat")

@bp.route("/api/web/translate", methods=["POST"])
@require_login
def translate_api():
    data = request.json or {}
    text = data.get("text")
    if not text: return jsonify({"error": "empty"}), 400
    prompt = f"Translate this exact text to English for an AI image generator: {text}"
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        res = loop.run_until_complete(ask(prompt, "translator", is_owner=False, mode="fast"))
        english = res.get("reply", text).strip().replace("`", "").replace("\n", " ")
        return jsonify({"english": english})
    except Exception:
        return jsonify({"english": text})

@bp.route("/api/web/ai_vision", methods=["POST"])
@require_login
def api_ai_vision():
    data = request.json or {}
    file_b64 = data.get("image")
    prompt = data.get("prompt", "حلل هذا الملف أو الصورة واوصفه بالتفصيل.")
    mime_type = data.get("mime_type", "image/jpeg")
    
    if not file_b64: return jsonify({"error": "لا توجد بيانات"}), 400
    if "," in file_b64:
        header, file_b64 = file_b64.split(",", 1)
        if "data:" in header and ";" in header:
            mime_type = header.split(":")[1].split(";")[0]
        
    async def _try_model(model_name):
        if not config.ai.gemini: return None, "no_key"
        try:
            async with httpx.AsyncClient(timeout=60) as c:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={config.ai.gemini}"
                payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": mime_type, "data": file_b64}}]}]}
                r = await c.post(url, json=payload)
                if r.status_code == 200:
                    return r.json()["candidates"][0]["content"]["parts"][0]["text"], None
                return None, f"{model_name} -> HTTP {r.status_code}"
        except Exception as e:
            return None, f"{model_name} -> {str(e)[:60]}"

    async def _run_vision():
        models_to_try = ["gemini-flash-lite-latest", "gemini-3.1-flash-lite", "gemini-3-flash-preview"]
        errs = []
        for model in models_to_try:
            res, err = await _try_model(model)
            if res: return {"ok": True, "reply": res, "model": model}
            if err: errs.append(err)
        return {"error": "فشل التحليل: " + ", ".join(errs)}
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(_run_vision())
    if result.get("ok"): return jsonify(result)
    return jsonify(result), 500

@bp.route("/api/web/ai_zip_analyze", methods=["POST"])
@require_login
def api_ai_zip_analyze():
    data = request.json or {}
    zip_b64 = data.get("zip")
    if not zip_b64: return jsonify({"error": "لا يوجد ملف"}), 400
    if "," in zip_b64: zip_b64 = zip_b64.split(",")[1]
    
    try:
        zip_data = base64.b64decode(zip_b64)
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "upload.zip")
        
        with open(zip_path, "wb") as f: f.write(zip_data)
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref: zip_ref.extractall(extract_dir)
            
        project_content = ""
        allowed_ext = ['.py', '.js', '.html', '.css', '.json', '.txt', '.md', '.sql', '.env.example']
        ignore_dirs = ['venv', '__pycache__', 'node_modules', '.git', 'env', 'dist', 'build']
        
        for root, dirs, files in os.walk(extract_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                if any(file.endswith(ext) for ext in allowed_ext):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, extract_dir)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            project_content += "\n\n# FILE: " + rel_path + "\n"
                            project_content += f.read()
                    except: pass
                    
        shutil.rmtree(temp_dir)
        if not project_content: return jsonify({"error": "لم يتم العثور على أكواد مقروءة."}), 400
        if len(project_content) > 150000: project_content = project_content[:150000] + "\n\n... (تم قص باقي الملفات)"
            
        prompt = "أنت مساعد برمجي. هذا مشروعي الشخصي. اشرح لي مكونات هذا المشروع باختصار، ماذا يفعل كل ملف رئيسي، وكيف يمكنني تحسينه في المستقبل:\n" + project_content
        
        async def _try_model(model_name):
            if not config.ai.gemini: return None
            try:
                async with httpx.AsyncClient(timeout=90) as c:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={config.ai.gemini}"
                    r = await c.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                    if r.status_code == 200: return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            except: pass
            return None
            
        async def _run():
            for m in ["gemini-3.6-flash", "gemini-flash-lite-latest", "gemini-3.1-flash-lite"]:
                res = await _try_model(m)
                if res: return res
            return None
            
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        final_reply = loop.run_until_complete(_run())
        if not final_reply: return jsonify({"error": "فشل تحليل الكود."}), 500
        return jsonify({"ok": True, "reply": final_reply})
    except Exception as e:
        return jsonify({"error": "خطأ: " + str(e)}), 500

@bp.route("/api/web_chat", methods=["POST"])
@require_login
def api_chat():
    uid = get_uid()
    data = request.json or {}
    message = (data.get("message") or "").strip()
    if not message: return jsonify({"reply": "اكتب رسالة"}), 400
    mode = "fast"
    if data.get("search"): mode = "search"
    elif data.get("deep_think"): mode = "think"
    is_owner = bool(session.get("is_owner"))
    try:
        result = asyncio.run(ask(message, uid, is_owner, mode))
        return jsonify({"reply": result.get("reply", ""), "mode": mode, "provider": result.get("provider"), "error": result.get("error", False)})
    except Exception as e:
        return jsonify({"reply": "حصل خطأ، جرب تاني", "error": True}), 500

@bp.route("/api/web/chat/clear", methods=["POST"])
@require_login
def api_chat_clear():
    uid = get_uid()
    try:
        from ai import memory
        memory.clear(uid)
        return jsonify({"ok": True})
    except Exception as e: return jsonify({"error": str(e)}), 500
