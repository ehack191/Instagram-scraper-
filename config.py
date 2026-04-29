"""
config.py — All configuration for the userbot.
Copy .env.example to .env and fill in your values.
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Telegram API credentials (get from https://my.telegram.org) ──
    API_ID: int = int(os.getenv("TG_API_ID", "0"))
    API_HASH: str = os.getenv("TG_API_HASH", "")
    PHONE_NUMBER: str = os.getenv("TG_PHONE", "")  # e.g. +91XXXXXXXXXX

    # ── Target Telegram group (username or numeric ID) ──
    # Use @groupusername or a numeric ID like -1001234567890
    TARGET_GROUP: str = os.getenv("TG_TARGET_GROUP", "")

    # ── Only respond to these Telegram user IDs (your own ID) ──
    # Leave empty to allow anyone (not recommended)
    ALLOWED_USER_IDS: list[int] = [
        int(x) for x in os.getenv("TG_ALLOWED_IDS", "").split(",") if x.strip()
    ]

    # ── Instagram credentials ──
    IG_USERNAME: str = os.getenv("IG_USERNAME", "")
    IG_PASSWORD: str = os.getenv("IG_PASSWORD", "")

    # ── Scraping settings ──
    FOLLOWER_LIMIT: int = int(os.getenv("FOLLOWER_LIMIT", "50"))
    NICHE_RESULT_LIMIT: int = int(os.getenv("NICHE_RESULT_LIMIT", "5"))

    # ── Scheduler ──
    SCHEDULE_INTERVAL_HOURS: int = int(os.getenv("SCHEDULE_HOURS", "6"))

    # ── Persisted niche list (stored in niches.json) ──
    _NICHES_FILE = "niches.json"

    @classmethod
    def _load_niches(cls) -> list[str]:
        env_niches = [n.strip() for n in os.getenv("SCHEDULED_NICHES", "").split(",") if n.strip()]
        try:
            with open(cls._NICHES_FILE) as f:
                saved = json.load(f)
            return list(dict.fromkeys(env_niches + saved))  # dedupe, env first
        except FileNotFoundError:
            return env_niches

    @classmethod
    def _save_niches(cls, niches: list[str]):
        with open(cls._NICHES_FILE, "w") as f:
            json.dump(niches, f)

    SCHEDULED_NICHES: list[str] = []  # loaded at runtime below

    @classmethod
    def add_scheduled_niche(cls, niche: str):
        if niche not in cls.SCHEDULED_NICHES:
            cls.SCHEDULED_NICHES.append(niche)
            cls._save_niches(cls.SCHEDULED_NICHES)


# Load persisted niches at import time
Config.SCHEDULED_NICHES = Config._load_niches()
