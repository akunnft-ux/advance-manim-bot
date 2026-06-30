import json
import os
import random
from datetime import date

from config import HISTORY_FILE, MAX_HISTORY_ITEMS, TOPICS


def _load_json(path: str, default=None):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else []


def _save_json(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_history() -> list:
    return _load_json(HISTORY_FILE, [])


def save_history(history: list):
    if len(history) > MAX_HISTORY_ITEMS:
        history = history[-MAX_HISTORY_ITEMS:]
    _save_json(HISTORY_FILE, history)


def get_used_topics_today(history: list) -> set:
    today = date.today().isoformat()
    return {h["topik"] for h in history if h.get("tanggal") == today}


def is_duplicate(judul: str, history: list) -> bool:
    return any(h["judul"] == judul for h in history)


def pick_topic(history: list) -> str:
    used_today = get_used_topics_today(history)
    available = [t for t in TOPICS if t not in used_today]
    if not available:
        available = list(TOPICS.keys())
    return random.choice(available)
