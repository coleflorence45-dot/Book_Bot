# vinted.py — Vinted API wrapper (Books Bot)

import re
import time
import requests
from datetime import datetime
from config import VINTED_COOKIE

VINTED_HOME     = "https://www.vinted.co.uk/"
VINTED_API      = "https://www.vinted.co.uk/api/v2/catalog/items"
VINTED_USER_API = "https://www.vinted.co.uk/api/v2/users/{user_id}/items"
VINTED_ITEM_API = "https://www.vinted.co.uk/api/v2/items/{item_id}"

session = requests.Session()


def get_session_cookie():
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language":           "en-GB,en;q=0.9",
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
        time.sleep(2)
    except Exception as e:
        print(f"  Auto-session failed ({e}) — falling back to manual cookie")
        if VINTED_COOKIE and VINTED_COOKIE != "your_cookie_here":
            session.cookies.set("_vinted_fr_session", VINTED_COOKIE)

    session.headers.update({
        "Accept":           "application/json, text/plain, */*",
        "Referer":          VINTED_HOME,
        "X-Requested-With": "XMLHttpRequest",
    })


def refresh_session():
    print("  🔄 Refreshing session...")
    time.sleep(3)
    get_session_cookie()


def _do_request(url: str, params: dict, label: str) -> list:
    response = None
    try:
        response = session.get(url, params=params, timeout=10)
        print(f"  [{label}] HTTP {response.status_code}")
    except Exception as e:
        print(f"  [{label}] Request failed: {e}")
        return []

    if response.status_code == 403:
        print("  ⚠️  403 — refreshing session and retrying...")
        refresh_session()
        time.sleep(2)
        try:
            response = session.get(url, params=params, timeout=10)
            print(f"  [{label}] Retry HTTP {response.status_code}")
        except Exception as e:
            print(f"  [{label}] Retry failed: {e}")
            return []
        if response.status_code == 403:
            print("  ⚠️  Still 403 — Vinted may be rate limiting your IP. Try again later.")
            return []

    if not response.text or not response.text.strip():
        print(f"  [{label}] Empty response — skipping")
        return []

    try:
        data = response.json()
        return data.get("items", [])
    except Exception:
        print(f"  [{label}] Non-JSON response: {response.text[:200]}")
        return []


def fetch_listings(keyword: str, max_price: float) -> list:
    params = {
        "search_text": keyword,
        "price_to":    max_price,
        "order":       "newest_first",
        "per_page":    96,
    }
    return _do_request(VINTED_API, params, keyword)


def fetch_seller_listings(user_id: str, max_price: float) -> list:
    url    = VINTED_USER_API.format(user_id=user_id)
    params = {"per_page": 96, "order": "newest_first", "price_to": max_price}
    return _do_request(url, params, f"seller:{user_id}")


def extract_year_from_title(title: str):
    """
    Pull a publication year from a listing title.
    Detects all years 1700–2030 including decade references (1880s, 1960s).

    Hyphenated date ranges (e.g. "1837-1971", "Coins 1800-1900"):
      If the later year is > 1910, use the later year — the range describes
      coverage/content, not the publication date. "1837-1971" means published
      in/after 1971, not 1837.
      If both years are within 1700-1910, use the earlier (publication start).
    """
    exact  = [int(y) for y in re.findall(r'(?:c\.?\s*)?(?<!\d)((?:1[7-9]|20)\d{2})(?!\d)(?!-\d*[A-Za-z])', title)]
    decade = [int(y) for y in re.findall(r'\b((?:1[7-9]|20)\d0)s\b', title, re.IGNORECASE)]

    # Detect hyphenated year ranges like "1837-1971" or "1800-1900"
    ranges = re.findall(r'\b((?:1[7-9]|20)\d{2})-((?:1[7-9]|20)\d{2})\b', title)
    for y1_str, y2_str in ranges:
        y1, y2 = int(y1_str), int(y2_str)
        if y2 > 1910:
            # Later year is post-Victorian — range describes content span,
            # publication is modern. Use the later year.
            exact = [y for y in exact if y != y1]
            if y2 not in exact:
                exact.append(y2)

    candidates = exact + decade
    return min(candidates) if candidates else None


def fetch_item_detail(item_id: str) -> dict:
    """
    Fetch the full detail page for a single item to get the complete description.
    The catalog API often returns truncated or empty descriptions.
    Only called for items that pass initial scoring.
    """
    url = VINTED_ITEM_API.format(item_id=item_id)
    try:
        response = session.get(url, timeout=10)
        if response.status_code == 403:
            refresh_session()
            response = session.get(url, timeout=10)
        if not response.text or not response.text.strip():
            return {}
        data = response.json()
        return data.get("item", {})
    except Exception as e:
        print(f"  [detail] Could not fetch item {item_id}: {e}")
        return {}


def format_item(item: dict) -> dict:
    """
    Normalise a raw Vinted item dict into a clean book-centric structure.
    All downstream modules use this shape.
    """
    photo_url  = ""
    photo_urls = []
    photos = item.get("photos") or []
    if photos:
        photo_url  = photos[0].get("url", "")
        photo_urls = [p.get("url", "") for p in photos if p.get("url")]
    elif isinstance(item.get("photo"), dict):
        photo_url  = item["photo"].get("url", "")
        photo_urls = [photo_url] if photo_url else []

    title       = item.get("title", "")
    description = item.get("description", "")

    raw_price = item.get("price", {})
    if isinstance(raw_price, dict):
        price = float(raw_price.get("amount", 0))
    else:
        price = float(raw_price or 0)

    seller     = item.get("user", {}).get("login", "unknown")
    seller_id  = str(item.get("user", {}).get("id", "0"))
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

    year_hint  = extract_year_from_title(title) or extract_year_from_title(description)
    favourites = int(item.get("favourite_count", 0) or item.get("favorites_count", 0) or 0)

    # Extract ISBN field if Vinted returns one — field names vary by API version
    isbn = (
        item.get("isbn") or
        item.get("isbn_number") or
        item.get("isbn13") or
        item.get("isbn10") or
        item.get("book_isbn") or
        ""
    )
    if isbn:
        print(f"  [vinted] ISBN field found: {isbn}")

    # Calculate listing age in minutes
    created_at  = item.get("created_at_ts") or item.get("created_at") or ""
    listing_age = None
    if created_at:
        try:
            from datetime import timezone
            if isinstance(created_at, (int, float)):
                listed_time = datetime.fromtimestamp(created_at, tz=timezone.utc)
            else:
                listed_time = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
            listing_age = int((datetime.now(tz=timezone.utc) - listed_time).total_seconds() / 60)
        except Exception:
            listing_age = None

    return {
        "id":            item["id"],
        "title":         title,
        "description":   description,
        "isbn":          isbn,
        "price":         price,
        "url":           f"https://www.vinted.co.uk/items/{item['id']}",
        "photo":         photo_url,
        "photo_urls":    photo_urls,
        "condition":     condition,
        "seller":        seller,
        "seller_id":     seller_id,
        "seller_rep":    seller_rep,
        "year_hint":     year_hint,
        "favourites":    favourites,
        "listing_age":   listing_age,
        "signals":       [],
        "score":         0,
        "image_verdict": None,
    }