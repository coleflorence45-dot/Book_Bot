# image_cache.py — persists image analysis results so items are never re-analysed
#
# Keyed by Vinted item ID. Stores verdict and timestamp.
# Survives seen_items.txt being cleared — no duplicate API costs.

import json
import os
from datetime import datetime

CACHE_FILE = "image_cache.json"


def load_cache() -> dict:
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cache(cache: dict):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def get_cached_verdict(item_id: str) -> dict | None:
    """Return cached verdict if this item has been analysed before, else None."""
    cache = load_cache()
    return cache.get(str(item_id))


def cache_verdict(item_id: str, verdict: dict):
    """Store image analysis result for this item ID."""
    cache = load_cache()
    cache[str(item_id)] = {
        "action":    verdict.get("action"),
        "reason":    verdict.get("reason"),
        "analysed":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    save_cache(cache)