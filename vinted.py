# vinted.py — Vinted API wrapper (Books Bot)

import re
import requests
from config import VINTED_COOKIE

VINTED_API = "https://www.vinted.co.uk/api/v2/catalog/items"

session = requests.Session()


def get_session_cookie():
    """Attach the Vinted session cookie and browser-like headers."""
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept":          "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer":         "https://www.vinted.co.uk/",
        "Cookie":          VINTED_COOKIE,
    })


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
        data = response.json()
        return data.get("items", [])
    except Exception as e:
        print(f"  Error fetching '{keyword}': {e}")
        return []


def extract_year_from_title(title: str):
    """
    Try to pull a publication year from the listing title.
    Handles both exact years (1877) and decade references (1930s, 1880s).
    Returns the earliest found year, or None.
    """
    # Exact 4-digit years — e.g. "1877", "1965"
    exact = [int(y) for y in re.findall(r'\b(1[7-9]\d{2}|200\d|201\d)\b', title)]

    # Decade references — e.g. "1930s", "1880s", "1960s"
    # Strip the 's' and treat as the start of that decade
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

    # Vinted nests price differently across API versions
    raw_price = item.get("price", {})
    if isinstance(raw_price, dict):
        price = float(raw_price.get("amount", 0))
    else:
        price = float(raw_price or 0)

    # Seller info
    seller      = item.get("user", {}).get("login", "unknown")
    seller_rep  = item.get("user", {}).get("feedback_reputation", 0)

    # Condition label
    condition_map = {
        6: "new with tags",
        5: "new without tags",
        4: "very good",
        3: "good",
        2: "satisfactory",
        1: "poor",
    }
    condition_id  = item.get("status_id", 0)
    condition     = condition_map.get(condition_id, item.get("status", "unknown"))

    year_hint = extract_year_from_title(title) or extract_year_from_title(description)

    return {
        "id":          item["id"],
        "title":       title,
        "description": description,
        "price":       price,
        "url":         f"https://www.vinted.co.uk/items/{item['id']}",
        "photo":       photo_url,
        "condition":   condition,
        "seller":      seller,
        "seller_rep":  seller_rep,
        "year_hint":   year_hint,   # extracted publication year (or None)
        "signals":     [],          # filled in by scorer.py
        "score":       0,           # filled in by scorer.py
        "image_verdict": None,      # filled in by image_analyser.py
    }