"""Proxy Manager — جلب وفحص"""
import random
import urllib.request
from database.connection import get_db
from logger import get_logger

log = get_logger("scraper.proxies")
db = get_db()

SOURCES = [
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
]

def fetch_free_proxies_sync() -> list:
    """جلب بروكسيات (sync - للاختبار)"""
    all_proxies = []
    for url in SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as r:
                text = r.read().decode('utf-8', errors='ignore')
                for line in text.strip().split('\n'):
                    line = line.strip()
                    if ':' in line and len(line.split(':')) == 2:
                        host, port = line.split(':')
                        if port.isdigit():
                            all_proxies.append(f"{host}:{port}")
        except Exception as e:
            log.warning(f"Fetch {url[:40]}: {str(e)[:50]}")
    return list(set(all_proxies))

def save_proxies(proxies: list) -> int:
    """يحفظ في DB"""
    inserted = 0
    for p in proxies[:500]:
        try:
            db.execute(
                "INSERT OR IGNORE INTO proxies (proxy_string, status, added_at) VALUES (?, 'ACTIVE', datetime('now'))",
                (p,), commit=True
            )
            inserted += 1
        except: pass
    log.info(f"Saved {inserted}/{len(proxies)} proxies")
    return inserted

def get_random_valid_proxy() -> str:
    """يرجع بروكسي شغال عشوائي"""
    rows = db.fetchall("SELECT proxy_string FROM proxies WHERE status='VALID' LIMIT 50")
    if not rows: return None
    return random.choice(rows)["proxy_string"]

def mark_valid(proxy_str: str, latency_ms: int = 0):
    db.execute("UPDATE proxies SET status='VALID', latency_ms=?, last_check=datetime('now') WHERE proxy_string=?",
               (latency_ms, proxy_str), commit=True)

def mark_dead(proxy_str: str):
    db.execute("UPDATE proxies SET status='DEAD', last_check=datetime('now') WHERE proxy_string=?",
               (proxy_str,), commit=True)

def stats() -> dict:
    total = db.fetchone("SELECT COUNT(*) as c FROM proxies")["c"]
    valid = db.fetchone("SELECT COUNT(*) as c FROM proxies WHERE status='VALID'")["c"]
    return {"total": total, "valid": valid, "dead": total - valid}
