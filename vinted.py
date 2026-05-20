# vinted.py — Vinted API wrapper (Books Bot)

import re
import time
import requests
from config import VINTED_COOKIE

VINTED_HOME = "https://www.vinted.co.uk/"
VINTED_API  = "https://www.vinted.co.uk/api/v2/catalog/items"

session = requests.Session()


def get_session_cookie():
    """
    Establish a real browser-like session by hitting the Vinted homepage first.
    This sets session cookies automatically, exactly as a browser would.
    Falls back to the manual VINTED_COOKIE from config if the auto-fetch fails.
    """
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language":           "en-GB,en;q=0.9",
        "Accept-Encoding":           "gzip, deflate, br",
        "Connection":                "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest":            "document",
        "Sec-Fetch-Mode":            "navigate",
        "Sec-Fetch-Site":            "none",
        "Sec-Fetch-User":            "?1",
    })

    try:
        resp = session.get(VINTED_HOME, timeout=15)
        print(f"  Session established (HTTP {resp.status_code})")
    except Exception as e:
        print(f"  Auto-session failed ({e}) — falling back to manual cookie")
        if VINTED_COOKIE and VINTED_COOKIE != "your_cookie_here":
            session.cookies.set("_vinted_fr_session", VINTED_COOKIE)

    # Switch to JSON API headers for all subsequent requests
    session.headers.update({
        "Accept":            "application/json, text/plain, */*",
        "Referer":           VINTED_HOME,
        "X-Requested-With":  "XMLHttpRequest",
    })


def refresh_session():
    """Re-hit the homepage to get fresh cookies — called automatically on 403."""
    print("  🔄 Refreshing session...")
    time.sleep(3)
    get_session_cookie()


def fetch_listings(keyword: str, max_price: float) -> list:
    """Return raw item dicts for a keyword, ordered newest first."""
    params = {
        "search_text": keyword,
        "price_to":    max_price,
        "order":       "newest_first",
        "per_page":    24,
    }
    try:
        response = session.get(VINTED_API, params=params, timeout=10)
        print(f"  [{keyword}] HTTP {response.status_code}")
        if response.status_code == 403:
            print("  ⚠️  403 — refreshing session and retrying...")
            refresh_session()
            time.sleep(2)
            response = session.get(VINTED_API, params=params, timeout=10)
            print(f"  [{keyword}] Retry HTTP {response.status_code}")
            if response.status_code == 403:
                print("  ⚠️  Still 403 — Vinted may be rate limiting your IP. Try again later.")
                return []
        data = response.json()
        return data.get("items", [])
    except Exception as e:
        print(f"  Error fetching '{keyword}': {e}")
        return []


def extract_year_from_title(title: str):
    """
    Pull a publication year from the listing title.
    Handles exact years (1877) and decade references (1880s, 1930s).
    Returns the earliest found year, or None.
    """
    exact  = [int(y) for y in re.findall(r'\b(1[7-9]\d{2}|200\d|201\d)\b', title)]
    decade = [int(y) for y in re.findall(r'\b(1[7-9]\d0|200\d)s\b', title, re.IGNORECASE)]
    candidates = exact + decade
    return min(candidates) if candidates else None


def format_item(item: dict) -> dict:
    """
    Normalise a raw Vinted item dict into a clean book-centric structure.
    All downstream modules (scorer, telegram_bot) use this shape.
    """
    photo_url = ""
    photos = item.get("photos") or []
    if photos:
        photo_url = photos[0].get("url", "")
    elif isinstance(item.get("photo"), dict):
        photo_url = item["photo"].get("url", "")

    title       = item.get("title", "")
    description = item.get("description", "")

    raw_price = item.get("price", {})
    if isinstance(raw_price, dict):
        price = float(raw_price.get("amount", 0))
    else:
        price = float(raw_price or 0)

    seller     = item.get("user", {}).get("login", "unknown")
    seller_rep = item.get("user", {}).get("feedback_reputation", 0)

    condition_map = {
        6: "new with tags",
        5: "new without tags",
        4: "very good",
        3: "good",
        2: "satisfactory",
        1: "poor",
    }
    condition_id = item.get("status_id", 0)
    condition    = condition_map.get(condition_id, item.get("status", "unknown"))

    year_hint = extract_year_from_title(title) or extract_year_from_title(description)

    return {
        "id":            item["id"],
        "title":         title,
        "description":   description,
        "price":         price,
        "url":           f"https://www.vinted.co.uk/items/{item['id']}",
        "photo":         photo_url,
        "condition":     condition,
        "seller":        seller,
        "seller_rep":    seller_rep,
        "year_hint":     year_hint,
        "signals":       [],
        "score":         0,
        "image_verdict": None,
    }