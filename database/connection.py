"""DB Connection — Bulletproof SQLite (No More Locked Errors)"""
import sqlite3
import threading
import shutil
import time
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
from config import config
from logger import get_logger

log = get_logger("db")
_lock = threading.RLock()
_conn = None

class Database:
    def __init__(self, path=None):
        self.path = path or config.paths.db_path
        self._ensure_dir()

    def _ensure_dir(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self):
        global _conn
        if _conn is None:
            for attempt in range(3):
                try:
                    _conn = sqlite3.connect(
                        str(self.path),
                        timeout=60, # زيادة وقت الانتظار لـ 60 ثانية
                        check_same_thread=False,
                        isolation_level=None # Auto-commit mode لمنع التعليق
                    )
                    _conn.row_factory = sqlite3.Row
                    # إعدادات WAL Mode للسماح بالقراءة والكتابة في نفس الوقت
                    _conn.execute("PRAGMA journal_mode=WAL")
                    _conn.execute("PRAGMA synchronous=NORMAL")
                    _conn.execute("PRAGMA foreign_keys=ON")
                    _conn.execute("PRAGMA busy_timeout=60000") # انتظر 60 ثانية قبل ما تقول مقفولة
                    log.info(f"Connected: {self.path.name}")
                    return _conn
                except sqlite3.OperationalError as e:
                    log.warning(f"Connect attempt {attempt+1} failed: {e}")
                    time.sleep(1)
            raise RuntimeError("Failed to connect to DB after 3 attempts")
        return _conn

    def execute(self, query, params=(), commit=False):
        with _lock:
            conn = self._connect()
            # ═══ نظام حماية (Retry) لو الداتابيز اتقفلت لجزء من الثانية ═══
            retries = 5
            while retries > 0:
                try:
                    cur = conn.execute(query, params)
                    if commit:
                        conn.commit()
                    return cur
                except sqlite3.OperationalError as e:
                    if "locked" in str(e).lower():
                        log.debug("DB Locked, retrying in 0.5s...")
                        time.sleep(0.5)
                        retries -= 1
                    else:
                        raise e
            raise Exception("Database is permanently locked, please try again.")

    def executemany(self, query, params_list, commit=True):
        with _lock:
            conn = self._connect()
            retries = 5
            while retries > 0:
                try:
                    cur = conn.executemany(query, params_list)
                    if commit: conn.commit()
                    return cur
                except sqlite3.OperationalError as e:
                    if "locked" in str(e).lower():
                        time.sleep(0.5)
                        retries -= 1
                    else: raise e
            raise Exception("Database is permanently locked.")

    def fetchone(self, query, params=()):
        cur = self.execute(query, params)
        return cur.fetchone()

    def fetchall(self, query, params=()):
        cur = self.execute(query, params)
        return cur.fetchall()

    def executescript(self, script, commit=True):
        with _lock:
            conn = self._connect()
            conn.executescript(script)
            if commit: conn.commit()

    @contextmanager
    def transaction(self):
        with _lock:
            conn = self._connect()
            try:
                conn.execute("BEGIN IMMEDIATE") # BEGIN IMMEDIATE بيمنع التعليق
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def ping(self) -> bool:
        try:
            self.execute("SELECT 1").fetchone()
            return True
        except Exception:
            return False

    def backup(self, dest=None) -> str:
        dest = dest or self.path.parent / f"{self.path.stem}_backup_{datetime.now():%Y%m%d_%H%M%S}.db"
        try:
            with _lock:
                conn = self._connect()
                conn.commit()
                shutil.copy2(self.path, dest)
            return str(dest)
        except Exception as e:
            return ""

    def close(self):
        global _conn
        with _lock:
            if _conn:
                _conn.close()
                _conn = None

_db = None
def get_db() -> Database:
    global _db
    if _db is None:
        _db = Database()
    return _db
