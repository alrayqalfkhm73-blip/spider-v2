"""Session Pool — اختيار أفضل جلسة + تتبع الأداء"""
from database.connection import get_db
from database.queries import sessions as sess_q
from logger import get_logger

log = get_logger("scraper.sessions")
db = get_db()

class SessionInfo:
    def __init__(self, name, user_id, daily_pumped, last_pump_date):
        self.name = name
        self.user_id = user_id
        self.daily_pumped = daily_pumped or 0
        self.last_pump_date = last_pump_date
        self.successes = 0
        self.failures = 0

    @property
    def score(self) -> int:
        total = self.successes + self.failures
        if total == 0: return 50
        return int((self.successes / total) * 100)

    @property
    def is_alive(self) -> bool:
        return self.score > 0

class SessionPool:
    """يدير كل جلسات المستخدم أو المالك"""

    def __init__(self, owner_id: str, is_owner: bool = False):
        self.owner_id = str(owner_id)
        self.is_owner = is_owner
        self._stats = {}  # name -> SessionInfo

    def load(self) -> list:
        """يرجع كل الجلسات الشغالة مرتبة"""
        if self.is_owner:
            rows = db.fetchall("SELECT session_name, user_id, daily_pumped, last_pump_date, status FROM sessions")
        else:
            rows = db.fetchall(
                "SELECT session_name, user_id, daily_pumped, last_pump_date, status FROM sessions WHERE user_id=?",
                (self.owner_id,)
            )

        result = []
        for r in rows:
            info = self._stats.get(r["session_name"])
            if not info:
                info = SessionInfo(r["session_name"], r["user_id"], r["daily_pumped"], r["last_pump_date"])
                self._stats[r["session_name"]] = info
            result.append(info)

        result.sort(key=lambda s: s.score, reverse=True)
        return result

    def get_best(self) -> SessionInfo:
        """أعلى score"""
        pool = self.load()
        return pool[0] if pool else None

    def track_result(self, session_name: str, success: bool):
        """يسجل نتيجة عملية"""
        info = self._stats.get(session_name)
        if not info:
            info = SessionInfo(session_name, self.owner_id, 0, None)
            self._stats[session_name] = info
        if success:
            info.successes += 1
        else:
            info.failures += 1

    def get_session_path(self, session_name: str) -> str:
        from config import config
        return str(config.paths.sessions_dir / session_name)

    def daily_limit_ok(self, session_name: str, limit: int = 40) -> bool:
        return sess_q.daily_limit_check(session_name, limit)
