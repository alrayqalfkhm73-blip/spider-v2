"""Route dependencies"""
from functools import wraps
from flask import session, redirect, request, jsonify
from config import config

def require_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "unauthorized"}), 401
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

def require_owner(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return jsonify({"error": "unauthorized"}), 401
        if not session.get("is_owner"):
            return jsonify({"error": "forbidden"}), 403
        return f(*args, **kwargs)
    return wrapper

def get_uid() -> str:
    if session.get("is_owner"):
        return str(config.telegram.owner_id)
    return str(session.get("user_id") or "")
