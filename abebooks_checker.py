# abebooks_checker.py — Market value lookup via AbeBooks search
#
# Searches AbeBooks for the listing title and scrapes the lowest asking price
# from the first few results. If the Vinted price is significantly below market,
# fires a special CONFIRMED FLIP signal.
#
# No API key needed — scrapes the public search page.

import re
import requests

ABEBOOKS_SEARCH = "https://www.abebooks.co.uk/servlet/SearchResults"
FLIP_THRESHOLD  = 3.0   # Vinted price must be less than 1/3 of AbeBooks price to confirm

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-GB,en;q=0.9",
}


def _clean_title(title: str) -> str:
    """Strip common noise words for a cleaner search query."""
    noise = [
        "hardback", "hardcover", "paperback", "softback", "vintage",
        "antique", "old", "illustrated", "book", "first edition",
        "1st edition", "rare", "collectible",
    ]
    cleaned = title.lower()
    for word in noise:
        cleaned = cleaned.replace(word, "")
    # Keep only meaningful words, max 6
    words = [w for w in cleaned.split() if len(w) > 3][:6]
    return " ".join(words)


def _extract_prices(html: str) -> list:
    """Extract GBP prices from AbeBooks search results HTML."""
    # Matches patterns like £12.50 or £120.00
    raw = re.findall(r'£([\d,]+\.?\d*)', html)
    prices = []
    for p in raw:
        try:
            prices.append(float(p.replace(",", "")))
        except ValueError:
            continue
    return prices


def check_market_value(item: dict) -> dict:
    """
    Search AbeBooks for the item title and return a market value assessment.

    Returns dict with:
        found         (bool)   — whether results were found
        lowest_price  (float)  — lowest AbeBooks asking price in £
        median_price  (float)  — median asking price
        confirmed_flip (bool)  — True if Vinted price < 1/3 of AbeBooks price
        multiple      (float)  — how many times more expensive AbeBooks is
        search_title  (str)    — what was searched
    """
    default = {
        "found": False, "lowest_price": 0, "median_price": 0,
        "confirmed_flip": False, "multiple": 0, "search_title": "",
    }

    title = item.get("title", "")
    if not title:
        return default

    search_query = _clean_title(title)
    if not search_query:
        return default

    # Add year to query if known, otherwise add antiquarian terms
    year_hint = item.get("year_hint")
    if year_hint and 1800 <= year_hint <= 1898:
        search_query = f"{search_query} {year_hint}"
    else:
        search_query = f"{search_query} victorian antique"

    params = {
        "kn":    search_query,
        "sts":   "t",
        "cm_sp": "SearchF-_-TopNavISS-_-Results",
        "bx":    "on",          # Antiquarian & Collectible filter
        "fe":    "on",          # First editions filter
        "yrh":   "1899",        # Year published — up to 1899
        "sortby": "1",          # Sort by price (lowest first for floor finding)
    }

    try:
        resp = requests.get(
            ABEBOOKS_SEARCH, params=params,
            headers=headers, timeout=10
        )
        if not resp.ok:
            return default

        prices = _extract_prices(resp.text)
        if not prices:
            return default

        prices.sort()
        # Filter out suspiciously low prices — likely modern reprints slipping through
        # Victorian antiquarian books rarely sell for under £5 on AbeBooks
        prices = [p for p in prices if p >= 5.0]
        if not prices:
            return default

        lowest = prices[0]
        median = prices[len(prices) // 2]
        vinted_price = float(item.get("price", 999))
        multiple     = round(lowest / vinted_price, 1) if vinted_price > 0 else 0
        confirmed    = vinted_price > 0 and (lowest / vinted_price) >= FLIP_THRESHOLD

        return {
            "found":          True,
            "lowest_price":   lowest,
            "median_price":   median,
            "confirmed_flip": confirmed,
            "multiple":       multiple,
            "search_title":   search_query,
        }

    except Exception as e:
        print(f"  [abebooks] Lookup failed: {e}")
        return default