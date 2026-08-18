"""
Simple, file-backed rate limiting to protect your free Gemini quota.

Two independent daily caps, both reset automatically at midnight (a new
date key just starts counting from zero):
  - a GLOBAL cap: total requests across every visitor, all day
  - a PER-SESSION cap: stops one visitor from eating the whole global quota

State is saved to a small JSON file (config.RATE_LIMIT_STATE_PATH) so
counts survive a server restart — important since free hosting tiers
occasionally restart your app.
"""
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Dict

from . import config


class RateLimitExceeded(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def _today() -> str:
    return date.today().isoformat()


def _load_state() -> Dict:
    path: Path = config.RATE_LIMIT_STATE_PATH
    if not path.exists():
        return {"global": {}, "per_session": {}}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"global": {}, "per_session": {}}


def _save_state(state: Dict) -> None:
    path: Path = config.RATE_LIMIT_STATE_PATH
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f)


def check_and_increment(action: str, session_id: str, global_limit: int, session_limit: int) -> None:
    """
    Raises RateLimitExceeded if either cap has been hit for this action.
    Otherwise increments both counters and saves state to disk.
    `action` namespaces the caps (e.g. "chat" vs "upload" get separate budgets).
    """
    today = _today()
    state = _load_state()

    global_counts = state["global"].setdefault(action, {})
    session_counts = state["per_session"].setdefault(action, {}).setdefault(session_id, {})

    global_today = global_counts.get(today, 0)
    session_today = session_counts.get(today, 0)

    if global_limit > 0 and global_today >= global_limit:
        raise RateLimitExceeded(
            "This demo has hit its daily limit for this action. Please try again tomorrow."
        )
    if session_limit > 0 and session_today >= session_limit:
        raise RateLimitExceeded(
            f"You've hit today's per-user limit ({session_limit}). Please try again tomorrow."
        )

    global_counts[today] = global_today + 1
    session_counts[today] = session_today + 1
    _save_state(state)
