"""Cache — 500ms للاستعلامات المتكررة"""
import time
import threading
from typing import Any, Optional, Callable

class TTLCache:
    def __init__(self, ttl_ms: int = 500, max_size: int = 1000):
        self.ttl = ttl_ms / 1000.0
        self.max_size = max_size
        self._data = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._data:
                value, expires = self._data[key]
                if time.time() < expires:
                    return value
                del self._data[key]
            return None

    def set(self, key: str, value: Any):
        with self._lock:
            if len(self._data) >= self.max_size:
                # حذف أقدم عنصر
                oldest = min(self._data.items(), key=lambda x: x[1][1])[0]
                del self._data[oldest]
            self._data[key] = (value, time.time() + self.ttl)

    def get_or_set(self, key: str, factory: Callable[[], Any]) -> Any:
        cached = self.get(key)
        if cached is not None:
            return cached
        value = factory()
        self.set(key, value)
        return value

    def invalidate(self, prefix: str = ""):
        with self._lock:
            if prefix:
                self._data = {k: v for k, v in self._data.items() if not k.startswith(prefix)}
            else:
                self._data.clear()

user_cache = TTLCache(ttl_ms=500, max_size=500)
stats_cache = TTLCache(ttl_ms=2000, max_size=100)
