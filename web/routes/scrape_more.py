"""Scrape groups list + Vault"""
from flask import Blueprint, jsonify, request, Response
import csv
import io
from web.deps import require_login, get_uid
from database.queries import sessions as sess_q, members as members_q
from database.connection import get_db
from logger import get_logger

bp = Blueprint("scrape_more", __name__)
log = get_logger("web.scrape_more")
db = get_db()

_groups_cache = {}  # uid -> {groups, ts}
CACHE_TTL = 300  # 5 minutes

@bp.route("/api/web/scrape/groups")
@require_login
def scrape_groups():
    import time
    uid = get_uid()

    # Cache 5 min
    cached = _groups_cache.get(uid)
    if cached and time.time() - cached["ts"] < 300:
        return jsonify({"groups": cached["groups"], "cached": True})

    session = sess_q.get_active(uid)
    if not session:
        all_sess = sess_q.get_all(uid)
        session = all_sess[0] if all_sess else None

    if not session:
        return jsonify({"error": "مفيش جلسة مربوطة", "groups": []})

    from config import config
    from pathlib import Path as P
    sess_name = str(session["session_name"]).replace(".session", "")
    sess_path = str(config.paths.sessions_dir / sess_name)

    if not P(sess_path + ".session").exists():
        return jsonify({"error": "ملف الجلسة مش موجود", "groups": []})

    groups = []
    try:
        import asyncio
        from pyrogram import Client, enums

        async def _load():
            cli = Client(sess_path, api_id=config.telegram.api_id,
                        api_hash=config.telegram.api_hash, no_updates=True)
            try:
                await asyncio.wait_for(cli.connect(), timeout=20)
                async def _scan():
                    async for d in cli.get_dialogs(limit=100):
                        if d.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL]:
                            groups.append({
                                "id": d.chat.id,
                                "title": d.chat.title or "بدون اسم",
                                "type": "channel" if d.chat.type == enums.ChatType.CHANNEL else "group",
                                "members": getattr(d.chat, "members_count", 0) or 0,
                            })
                await asyncio.wait_for(_scan(), timeout=60)
            finally:
                try: await cli.disconnect()
                except: pass

        asyncio.run(_load())
        _groups_cache[uid] = {"groups": groups, "ts": time.time()}
        log.info(f"Loaded {len(groups)} groups for {uid}")
        return jsonify({"groups": groups, "cached": False})
    except Exception as e:
        log.error(f"Load groups failed: {str(e)[:100]}")
        return jsonify({"error": f"فشل: {str(e)[:80]}", "groups": []})

@bp.route("/api/web/vault/list")
@require_login
def vault_list():
    uid = get_uid()
    limit = int(request.args.get("limit", 20))
    page = int(request.args.get("page", 1))
    search = request.args.get("search", "").strip()
    filter_type = request.args.get("filter", "all")
    
    offset = (page - 1) * limit
    
    query = "SELECT * FROM members WHERE owner_user_id=?"
    params = [str(uid)]
    
    if search:
        query += " AND (username LIKE ? OR user_id LIKE ? OR id LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
        
    if filter_type == "with_username":
        query += " AND username IS NOT NULL AND username != ''"
    elif filter_type == "without_username":
        query += " AND (username IS NULL OR username = '')"
        
    count_query = query.replace("SELECT *", "SELECT COUNT(*) as c")
    total = db.fetchone(count_query, tuple(params))["c"]
    
    query += " ORDER BY rowid DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    rows = db.fetchall(query, tuple(params))
    members = [dict(r) for r in rows]
    
    return jsonify({"total": total, "members": members, "page": page, "limit": limit})



@bp.route("/api/web/vault/export")
@require_login
def vault_export():
    uid = get_uid()
    members = db.fetchall("SELECT username, user_id FROM members WHERE owner_user_id=?", (str(uid),))
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Username', 'User_ID'])
    
    for m in members:
        writer.writerow([m['username'] or '', m['user_id'] or ''])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=spider_vault_{uid}.csv"}
    )


@bp.route("/api/web/vault/clean", methods=["POST"])
@require_login
def vault_clean():
    uid = get_uid()
    data = request.json or {}
    action = data.get("action")
    
    if action == "no_username":
        cur = db.execute("DELETE FROM members WHERE owner_user_id=? AND (username IS NULL OR username = '')", (str(uid),), commit=True)
        deleted = cur.rowcount
    elif action == "duplicates":
        # حذف المكرر بناءً على user_id
        cur = db.execute("""
            DELETE FROM members 
            WHERE rowid NOT IN (
                SELECT MIN(rowid) FROM members WHERE owner_user_id=? GROUP BY user_id
            ) AND owner_user_id=?
        """, (str(uid), str(uid)), commit=True)
        deleted = cur.rowcount
    else:
        return jsonify({"error": "إجراء غير معروف"}), 400
        
    return jsonify({"ok": True, "deleted": deleted})

@bp.route("/api/web/vault/sources")
@require_login
def vault_sources():
    uid = get_uid()
    rows = db.fetchall("SELECT scraped_from, COUNT(*) as c FROM members WHERE owner_user_id=? GROUP BY scraped_from ORDER BY c DESC LIMIT 5", (str(uid),))
    return jsonify({"sources": [dict(r) for r in rows]})

@bp.route("/api/web/vault/stats")
@require_login
def vault_stats():
    uid = get_uid()
    return jsonify(members_q.stats_by_owner(uid))
