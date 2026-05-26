# seller_watchlist.py — tracks sellers who produced bought alerts
# Auto-removes sellers that return 404 three consecutive scans in a row.

import json
import os
from datetime import datetime

WATCHLIST_FILE = "seller_watchlist.json"
MAX_404s       = 3   # remove seller after this many consecutive 404s


def load_watchlist() -> dict:
    if not os.path.exists(WATCHLIST_FILE):
        return {}
    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_watchlist(watchlist: dict):
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(watchlist, f, indent=2, ensure_ascii=False)


def add_seller(item: dict):
    """Add or update a seller when ✅ Bought is tapped in Telegram."""
    seller_id = str(item.get("seller_id", ""))
    seller    = item.get("seller", "unknown")
    title     = item.get("title", "")

    if not seller_id or seller_id == "0":
        return

    watchlist = load_watchlist()

    if seller_id in watchlist:
        watchlist[seller_id]["buy_count"] += 1
        watchlist[seller_id]["titles"].append(title)
        watchlist[seller_id]["last_seen"]    = datetime.now().strftime("%Y-%m-%d %H:%M")
        watchlist[seller_id]["consecutive_404s"] = 0   # reset on re-add
    else:
        watchlist[seller_id] = {
            "username":         seller,
            "user_id":          seller_id,
            "added":            datetime.now().strftime("%Y-%m-%d %H:%M"),
            "last_seen":        datetime.now().strftime("%Y-%m-%d %H:%M"),
            "buy_count":        1,
            "titles":           [title],
            "consecutive_404s": 0,
        }
        print(f"  👁️  Added {seller} to seller watchlist")

    save_watchlist(watchlist)


def record_404(seller_id: str) -> bool:
    """
    Increment 404 counter for a seller.
    Returns True if the seller was removed (hit MAX_404s).
    """
    watchlist = load_watchlist()
    sid       = str(seller_id)

    if sid not in watchlist:
        return False

    watchlist[sid]["consecutive_404s"] = watchlist[sid].get("consecutive_404s", 0) + 1

    if watchlist[sid]["consecutive_404s"] >= MAX_404s:
        username = watchlist[sid].get("username", sid)
        del watchlist[sid]
        save_watchlist(watchlist)
        print(f"  🗑️  Removed {username} from watchlist (404 × {MAX_404s})")
        return True

    save_watchlist(watchlist)
    return False


def record_success(seller_id: str):
    """Reset 404 counter when a seller's listings are fetched successfully."""
    watchlist = load_watchlist()
    sid       = str(seller_id)
    if sid in watchlist:
        watchlist[sid]["consecutive_404s"] = 0
        watchlist[sid]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_watchlist(watchlist)


def get_watched_sellers() -> list:
    """Return list of (user_id, username) tuples for all watched sellers."""
    watchlist = load_watchlist()
    return [(sid, data["username"]) for sid, data in watchlist.items()]