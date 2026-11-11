"""Proxies"""
from flask import Blueprint, jsonify
from web.deps import require_login
from scraper.proxy_manager import fetch_free_proxies_sync, save_proxies, stats as pstats
from database.connection import get_db

bp = Blueprint("proxies", __name__)
db = get_db()

@bp.route("/api/web/proxies/list")
@require_login
def list_proxies():
    rows = db.fetchall("SELECT proxy_string, status, latency_ms FROM proxies ORDER BY id DESC LIMIT 100")
    return jsonify({"proxies": [dict(r) for r in rows]})

@bp.route("/api/web/proxies/fetch", methods=["POST"])
@require_login
def fetch_proxies():
    try:
        proxies = fetch_free_proxies_sync()
        count = save_proxies(proxies)
        return jsonify({"ok": True, "count": count, "total_fetched": len(proxies)})
    except Exception as e:
        return jsonify({"error": str(e)[:100]}), 500

@bp.route("/api/web/proxies/stats")
@require_login
def proxies_stats():
    return jsonify(pstats())
