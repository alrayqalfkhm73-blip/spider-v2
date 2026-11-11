"""Migrations — إضافة كل الأعمدة الناقصة بأمان"""
from datetime import datetime
from database.connection import get_db
from database.schema import table_exists, column_exists
from logger import get_logger

log = get_logger("migration")
db = get_db()
SCHEMA_VERSION = 1

# كل عمود قد يكون ناقصاً في الداتابيز القديمة
MISSING_COLUMNS = [
    # users
    ("users", "web_password", "TEXT"),
    ("users", "gift_streak", "INTEGER DEFAULT 0"),
    ("users", "last_gift_date", "TEXT"),
    ("users", "wheel_spins_today", "INTEGER DEFAULT 0"),
    ("users", "last_wheel_date", "TEXT"),
    ("users", "ban_reason", "TEXT"),
    ("users", "notes", "TEXT"),
    ("users", "daily_streak", "INTEGER DEFAULT 0"),
    ("users", "referrer_id", "TEXT"),
    ("users", "referral_count", "INTEGER DEFAULT 0"),
    ("users", "total_scraped", "INTEGER DEFAULT 0"),
    ("users", "total_pumped", "INTEGER DEFAULT 0"),
    ("users", "last_active", "TEXT"),
    ("users", "joined_at", "TEXT"),
    ("users", "last_gift", "TEXT"),
    # sessions
    ("sessions", "daily_pumped", "INTEGER DEFAULT 0"),
    ("sessions", "last_pump_date", "TEXT"),
    ("sessions", "is_enabled", "INTEGER DEFAULT 1"),
    ("sessions", "last_used", "TEXT"),
    ("sessions", "scrape_count", "INTEGER DEFAULT 0"),
    ("sessions", "pump_count", "INTEGER DEFAULT 0"),
    ("sessions", "user_id", "TEXT"),
    ("sessions", "session_path", "TEXT"),
    ("sessions", "status", "TEXT DEFAULT 'ACTIVE'"),
    ("sessions", "added_at", "TEXT"),
    # codes
    ("codes", "used_by", "TEXT"),
    ("codes", "expires_at", "TEXT"),
    ("codes", "max_uses", "INTEGER DEFAULT 1"),
    ("codes", "current_uses", "INTEGER DEFAULT 0"),
    ("codes", "used_at", "TEXT"),
    ("codes", "type", "TEXT DEFAULT 'VIP'"),
    # members
    ("members", "owner_user_id", "TEXT"),
    ("members", "username", "TEXT"),
    ("members", "user_id", "TEXT"),
    ("members", "status", "TEXT DEFAULT 'ACTIVE'"),
    ("members", "scraped_at", "TEXT"),
    ("members", "scraped_from", "TEXT"),
    # global_vault
    ("global_vault", "owner_user_id", "TEXT"),
    ("global_vault", "username", "TEXT"),
    ("global_vault", "user_id", "TEXT"),
    ("global_vault", "scraped_from", "TEXT"),
    ("global_vault", "added_at", "TEXT"),
    # banned
    ("banned", "reason", "TEXT"),
    ("banned", "banned_at", "TEXT"),
    ("banned", "ban_expires", "TEXT"),
    # proxies
    ("proxies", "latency_ms", "INTEGER DEFAULT 0"),
    ("proxies", "country", "TEXT"),
    ("proxies", "proxy_type", "TEXT DEFAULT 'http'"),
    ("proxies", "quality_score", "INTEGER DEFAULT 50"),
    ("proxies", "last_check", "TEXT"),
    ("proxies", "check_count", "INTEGER DEFAULT 0"),
    ("proxies", "session_name", "TEXT"),
]

def add_column_safe(table: str, column: str, type_def: str) -> bool:
    if not table_exists(table):
        return False
    if column_exists(table, column):
        return True
    try:
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}", commit=True)
        log.info(f"  + {table}.{column}")
        return True
    except Exception as e:
        log.debug(f"  skip {table}.{column}: {str(e)[:60]}")
        return False

def add_missing_columns() -> int:
    added = 0
    for table, col, typ in MISSING_COLUMNS:
        if add_column_safe(table, col, typ):
            added += 1
    log.info(f"Columns verified: {added}/{len(MISSING_COLUMNS)}")
    return added

def create_table_safe(name: str, sql: str) -> bool:
    if table_exists(name): return True
    try:
        db.execute(sql, commit=True)
        return True
    except Exception as e:
        log.error(f"Create table failed {name}: {e}")
        return False

def get_current_version() -> int:
    try:
        row = db.fetchone("SELECT MAX(version) as v FROM schema_version")
        return (row["v"] or 0) if row else 0
    except Exception:
        return 0

def apply_all():
    from database.schema import create_tables, create_indexes
    create_tables()
    add_missing_columns()
    create_indexes()
    try:
        if get_current_version() < SCHEMA_VERSION:
            db.execute("INSERT OR IGNORE INTO schema_version (version, applied_at) VALUES (?, ?)",
                       (SCHEMA_VERSION, datetime.now().strftime("%Y-%m-%d %H:%M:%S")), commit=True)
    except: pass
    log.info(f"Schema version: {SCHEMA_VERSION}")
    return True
