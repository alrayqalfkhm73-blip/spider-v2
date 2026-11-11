"""Spider V2 — Config Manager (v2.0.0)
Comprehensive configuration with sub-classes, validation, and health checks.
"""
import os
import re
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from dotenv import load_dotenv

CONFIG_VERSION = "2.0.0"

def _find_env():
    candidates = [
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent / "spider_bot" / ".env",
        Path("/root/spider_bot/.env"),
        Path("/root/.env"),
    ]
    for p in candidates:
        try:
            if p.exists(): return p
        except (PermissionError, OSError):
            continue
    return None
_env_path = _find_env()
if _env_path: load_dotenv(_env_path)

@dataclass
class TelegramConfig:
    api_id: int = 0
    api_hash: str = ""
    bot_token: str = ""
    owner_id: int = 0
    assistant_bot_token: str = ""

    def validate(self) -> List[Dict[str, str]]:
        errs = []
        if self.api_id <= 0: errs.append({"key": "API_ID", "reason": "must be int > 0"})
        if not self.api_hash: errs.append({"key": "API_HASH", "reason": "missing"})
        if not self.bot_token: errs.append({"key": "BOT_TOKEN", "reason": "missing"})
        elif not re.match(r"^\d+:[A-Za-z0-9_-]+$", self.bot_token):
            errs.append({"key": "BOT_TOKEN", "reason": "invalid format"})
        if self.owner_id <= 0: errs.append({"key": "OWNER_ID", "reason": "must be int > 0"})
        return errs

@dataclass
class AIConfig:
    groq: str = ""
    gemini: str = ""
    openrouter: str = ""
    nvidia: str = ""
    sambanova: str = ""

    def validate(self) -> List[Dict[str, str]]:
        errs = []
        if not self.groq and not self.gemini and not self.openrouter:
            errs.append({"key": "AI_KEYS", "reason": "at least one AI provider required"})
        return errs

@dataclass
class WebConfig:
    flask_secret: str = "spider_v2_secret_2026"
    web_port: int = 8090
    ai_port: int = 8091
    owner_web_pass: str = "Mahmoud..12"

@dataclass
class Paths:
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent)
    parent_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    db_path: Path = field(init=False)
    db_original: Path = field(init=False)
    sessions_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    env_file: Path = field(default=None)

    def __post_init__(self):
        self.db_path = self.parent_dir / "spider_data_v2.db"
        self.db_original = self.parent_dir / "spider_data.db"
        self.sessions_dir = self.parent_dir / "sessions_pool"
        self.logs_dir = self.base_dir / "logs"
        self.env_file = _env_path

@dataclass
class Features:
    enable_ai: bool = True
    enable_scraper: bool = True
    enable_payments: bool = False

class Config:
    def __init__(self):
        self.version = CONFIG_VERSION
        self.telegram = TelegramConfig(
            api_id=int(os.getenv("API_ID", "0")),
            api_hash=os.getenv("API_HASH", ""),
            bot_token=os.getenv("BOT_TOKEN", ""),
            owner_id=int(os.getenv("OWNER_ID", "0")),
            assistant_bot_token=os.getenv("ASSISTANT_BOT_TOKEN", "")
        )
        self.ai = AIConfig(
            groq=os.getenv("GROQ_API_KEY", ""),
            gemini=os.getenv("GEMINI_API_KEY", ""),
            openrouter=os.getenv("OPENROUTER_API_KEY", ""),
            nvidia=os.getenv("NVIDIA_API_KEY", ""),
            sambanova=os.getenv("SAMBANOVA_API_KEY", "")
        )
        self.web = WebConfig(
            flask_secret=os.getenv("FLASK_SECRET", "spider_v2_secret_2026"),
            owner_web_pass=os.getenv("OWNER_WEB_PASS", "Mahmoud..12")
        )
        self.paths = Paths()
        self.features = Features()
        self.env_mode = os.getenv("ENV_MODE", "prod").lower()

    def is_dev(self) -> bool: return self.env_mode == "dev"
    def is_prod(self) -> bool: return self.env_mode == "prod"

    def mask_secrets(self) -> Dict[str, str]:
        def mask(s):
            if not s: return "❌ missing"
            if len(s) <= 10: return "***masked***"
            return f"{s[:5]}...{s[-5:]}"
        return {
            "BOT_TOKEN": mask(self.telegram.bot_token),
            "API_HASH": mask(self.telegram.api_hash),
            "GROQ": mask(self.ai.groq),
            "GEMINI": mask(self.ai.gemini),
            "OPENROUTER": mask(self.ai.openrouter)
        }

    def validate_all(self) -> List[Dict[str, str]]:
        errs = []
        errs.extend(self.telegram.validate())
        errs.extend(self.ai.validate())
        return errs

    def validate(self) -> List[str]:
        return [e["key"] for e in self.validate_all()]

    def ensure_directories(self):
        self.paths.logs_dir.mkdir(parents=True, exist_ok=True)
        self.paths.sessions_dir.mkdir(parents=True, exist_ok=True)

    def backup_env(self) -> str:
        if not self.paths.env_file or not self.paths.env_file.exists():
            return "No .env to backup"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = self.paths.env_file.parent / f".env.backup_{ts}"
        shutil.copy2(self.paths.env_file, backup)
        return str(backup)

    def health_check(self) -> Dict[str, str]:
        return {
            "Telegram": "✅ OK" if self.telegram.api_id > 0 else "❌ Missing",
            "AI Providers": f"✅ {sum([bool(self.ai.groq), bool(self.ai.gemini), bool(self.ai.openrouter)])} active",
            "Web": f"✅ Port {self.web.web_port}",
            "DB": "✅ Exists" if self.paths.db_original.exists() else "⚠️ Missing (will create)"
        }

    def get_summary(self) -> str:
        return f"Spider V2 (v{self.version}) | ENV: {self.env_mode} | Owner: {self.telegram.owner_id} | Ports: {self.web.web_port}/{self.web.ai_port}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "telegram": asdict(self.telegram),
            "web": asdict(self.web),
            "env_mode": self.env_mode
        }

    def reload(self):
        global config
        config = Config()
        return config

config = Config()
