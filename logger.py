"""Spider V2 — Logger (Structured + Context)"""
import logging
import json
import time
import traceback
import contextvars
from logging.handlers import RotatingFileHandler
from config import config

# Context variables (auto-injected)
request_id_var = contextvars.ContextVar("request_id", default="-")
user_id_var = contextvars.ContextVar("user_id", default="-")

class ConsoleFormatter(logging.Formatter):
    ICONS = {
        logging.DEBUG: "🔵",
        logging.INFO: "🟢",
        logging.WARNING: "🟡",
        logging.ERROR: "🔴",
        logging.CRITICAL: "💀"
    }
    COLORS = {
        logging.DEBUG: "\033[94m",
        logging.INFO: "\033[92m",
        logging.WARNING: "\033[93m",
        logging.ERROR: "\033[91m",
        logging.CRITICAL: "\033[95m"
    }
    RESET = "\033[0m"

    def format(self, record):
        icon = self.ICONS.get(record.levelno, "")
        color = self.COLORS.get(record.levelno, "")
        req = request_id_var.get()
        usr = user_id_var.get()
        ctx = f" [{req}|{usr}]" if req != "-" or usr != "-" else ""
        return f"{color}{icon} {record.levelname:<8}{self.RESET} {record.name}{ctx}: {record.getMessage()}"

class JSONFormatter(logging.Formatter):
    def format(self, record):
        data = {
            "time": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
            "user_id": user_id_var.get()
        }
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)
        return json.dumps(data, ensure_ascii=False)

_initialized = False

def setup_logging():
    global _initialized
    if _initialized: return
    _initialized = True

    config.paths.logs_dir.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger("spider_v2")
    root.setLevel(logging.DEBUG if config.is_dev() else logging.INFO)

    # Console
    ch = logging.StreamHandler()
    ch.setFormatter(ConsoleFormatter())
    ch.setLevel(logging.DEBUG if config.is_dev() else logging.INFO)
    root.addHandler(ch)

    # Access file (all)
    fh = RotatingFileHandler(config.paths.logs_dir / "access.log", maxBytes=10*1024*1024, backupCount=3, encoding="utf-8")
    fh.setFormatter(JSONFormatter())
    fh.setLevel(logging.INFO)
    root.addHandler(fh)

    # Error file (only errors)
    eh = RotatingFileHandler(config.paths.logs_dir / "error.log", maxBytes=10*1024*1024, backupCount=3, encoding="utf-8")
    eh.setFormatter(JSONFormatter())
    eh.setLevel(logging.ERROR)
    root.addHandler(eh)

def get_logger(name):
    setup_logging()
    return logging.getLogger(f"spider_v2.{name}")

def log_startup():
    log = get_logger("startup")
    log.info("=" * 55)
    log.info(f"🕷️ Spider V2 Starting — {config.get_summary()}")
    log.info("=" * 55)

def log_shutdown():
    log = get_logger("shutdown")
    log.info("🛑 Spider V2 Shutting down gracefully...")

def log_traceback(e: Exception, context: str = ""):
    log = get_logger("error")
    log.error(f"Exception in {context}: {str(e)}", exc_info=True)

class timer:
    def __init__(self, name: str):
        self.name = name
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, *args):
        elapsed = time.time() - self.start
        get_logger("timer").debug(f"⏱️ {self.name} took {elapsed:.3f}s")
