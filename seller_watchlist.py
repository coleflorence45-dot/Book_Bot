# seller_watchlist.py — tracks sellers who have produced BUY alerts
# Every scan checks their active listings directly, not just keyword searches

import json
import os
from datetime import datetime

WATCHLIST_FILE = "seller_watchlist.json"


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
    """
    Add a seller to the watchlist when a BUY alert fires on their listing.
    Stores seller username, user ID, and the title that triggered the alert.
    """
    seller_id  = str(item.get("seller_id", ""))
    seller     = item.get("seller", "unknown")
    title      = item.get("title", "")

    if not seller_id or seller_id == "0":
        return

    watchlist = load_watchlist()

    if seller_id in watchlist:
        # Already watching — log this new find
        watchlist[seller_id]["buy_count"] += 1
        watchlist[seller_id]["titles"].append(title)
        watchlist[seller_id]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    else:
        watchlist[seller_id] = {
            "username":  seller,
            "user_id":   seller_id,
            "added":     datetime.now().strftime("%Y-%m-%d %H:%M"),
            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "buy_count": 1,
            "titles":    [title],
        }
        print(f"  👁️  Added {seller} to seller watchlist")

    save_watchlist(watchlist)


def get_watched_sellers() -> list:
    """Return list of (user_id, username) tuples for all watched sellers."""
    watchlist = load_watchlist()
    return [(sid, data["username"]) for sid, data in watchlist.items()]