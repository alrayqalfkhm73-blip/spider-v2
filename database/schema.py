"""Schema — 20 tables + indexes + helpers"""
from database.connection import get_db
from logger import get_logger

log = get_logger("schema")
db = get_db()

TABLES = ["users","sessions","codes","members","global_vault","banned","forced_channels",
          "stats","proxies","tasks","logs","failed_members","blacklist","user_settings",
          "daily_tasks","transactions","user_achievements","feedback","daily_box",
          "schema_version","debug_reports","activity_log"]

TABLES_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY, points INTEGER DEFAULT 0,
    role TEXT DEFAULT 'USER', vip_expiry TEXT,
    daily_streak INTEGER DEFAULT 0, last_gift TEXT,
    referrer_id TEXT, referral_count INTEGER DEFAULT 0,
    total_scraped INTEGER DEFAULT 0, total_pumped INTEGER DEFAULT 0,
    last_active TEXT, joined_at TEXT, web_password TEXT,
    ban_reason TEXT, notes TEXT, gift_streak INTEGER DEFAULT 0,
    last_gift_date TEXT, wheel_spins_today INTEGER DEFAULT 0,
    last_wheel_date TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
    user_id TEXT, session_name TEXT PRIMARY KEY, session_path TEXT,
    added_at TEXT, status TEXT DEFAULT 'ACTIVE',
    daily_pumped INTEGER DEFAULT 0, last_pump_date TEXT,
    is_enabled INTEGER DEFAULT 1, last_used TEXT,
    scrape_count INTEGER DEFAULT 0, pump_count INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS codes (
    code TEXT PRIMARY KEY, value INTEGER, type TEXT DEFAULT 'VIP',
    used_by TEXT, used_at TEXT, created_at TEXT,
    expires_at TEXT, max_uses INTEGER DEFAULT 1, current_uses INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS members (
    id TEXT, username TEXT, user_id TEXT,
    status TEXT DEFAULT 'ACTIVE', scraped_at TEXT,
    scraped_from TEXT, owner_user_id TEXT
);
CREATE TABLE IF NOT EXISTS global_vault (
    id TEXT, username TEXT, user_id TEXT, scraped_from TEXT,
    added_at TEXT, owner_user_id TEXT
);
CREATE TABLE IF NOT EXISTS banned (id TEXT PRIMARY KEY, reason TEXT, banned_at TEXT, ban_expires TEXT);
CREATE TABLE IF NOT EXISTS forced_channels (channel TEXT PRIMARY KEY, added_at TEXT);
CREATE TABLE IF NOT EXISTS stats (key TEXT PRIMARY KEY, value INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS proxies (
    id INTEGER PRIMARY KEY AUTOINCREMENT, proxy_string TEXT UNIQUE,
    status TEXT DEFAULT 'ACTIVE', session_name TEXT, added_at TEXT,
    latency_ms INTEGER DEFAULT 0, country TEXT, proxy_type TEXT DEFAULT 'http',
    quality_score INTEGER DEFAULT 50, last_check TEXT, check_count INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, action TEXT, target TEXT,
    run_at TEXT, status TEXT DEFAULT 'PENDING', created_at TEXT
);
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT, message TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS failed_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT, member_id TEXT, username TEXT,
    owner_user_id TEXT, target_group TEXT, reason TEXT, failed_at TEXT
);
CREATE TABLE IF NOT EXISTS blacklist (
    id TEXT, owner_user_id TEXT, reason TEXT, added_at TEXT
);
CREATE TABLE IF NOT EXISTS user_settings (
    user_id TEXT, key TEXT, value TEXT, PRIMARY KEY (user_id, key)
);
CREATE TABLE IF NOT EXISTS daily_tasks (
    user_id TEXT, task_id TEXT, date TEXT, completed_at TEXT, claimed INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, task_id, date)
);
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, type TEXT,
    amount INTEGER, description TEXT, balance_after INTEGER, created_at TEXT
);
CREATE TABLE IF NOT EXISTS user_achievements (
    user_id TEXT, achievement_id TEXT, unlocked_at TEXT,
    PRIMARY KEY (user_id, achievement_id)
);
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, type TEXT,
    message TEXT, status TEXT DEFAULT 'NEW', admin_reply TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS daily_box (user_id TEXT, date TEXT, PRIMARY KEY (user_id, date));
CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, applied_at TEXT);
CREATE TABLE IF NOT EXISTS debug_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, error TEXT, solution TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, action TEXT,
    details TEXT, admin_id TEXT, created_at TEXT
);
"""

INDEXES_SQL = """
CREATE INDEX IF NOT EXISTS idx_members_owner ON members(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_members_uid ON members(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_logs_type ON logs(event_type);
CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_log(user_id);
"""

def table_exists(name: str) -> bool:
    row = db.fetchone("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return row is not None

def column_exists(table: str, column: str) -> bool:
    if not table_exists(table): return False
    rows = db.fetchall(f"PRAGMA table_info({table})")
    return any(r["name"] == column for r in rows)

def create_tables():
    db.executescript(TABLES_SQL)
    log.info(f"Tables: {len(TABLES)} created/verified")

def create_indexes():
    for stmt in INDEXES_SQL.strip().split(";"):
        stmt = stmt.strip()
        if not stmt: continue
        try:
            db.execute(stmt)
        except Exception as e:
            log.debug(f"Index skip: {str(e)[:60]}")
    log.info("Indexes created")

def create_all():
    create_tables()
    # بعد الجداول، أضف الأعمدة الناقصة قبل ما ننشئ indexes
    try:
        from database.migrations import add_missing_columns
        add_missing_columns()
    except ImportError:
        pass
    create_indexes()

def reset_for_test():
    for t in TABLES:
        db.execute(f"DROP TABLE IF EXISTS {t}")
    create_all()
    log.info("Schema reset")
