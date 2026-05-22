# ebay_checker.py — Market value lookup via eBay completed/sold listings
#
# Searches eBay UK for SOLD listings of the book title to get real transaction
# prices rather than asking prices. Sold prices are more accurate than AbeBooks
# asking prices since they reflect what buyers actually paid.
#
# No API key needed — scrapes the public completed listings search page.

import re
import requests
from datetime import datetime

EBAY_SEARCH = "https://www.ebay.co.uk/sch/i.html"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

FLIP_THRESHOLD = 3.0   # Vinted price must be less than 1/3 of eBay sold price


def _clean_title(title: str) -> str:
    """Strip noise words for a cleaner search query."""
    noise = [
        "hardback", "hardcover", "paperback", "softback", "vintage",
        "antique", "old", "illustrated", "book", "rare", "collectible",
        "beautiful", "stunning", "decorative", "display",
    ]
    cleaned = title.lower()
    for word in noise:
        cleaned = cleaned.replace(word, " ")
    words = [w for w in cleaned.split() if len(w) > 3][:6]
    return " ".join(words)


def _extract_sold_prices(html: str) -> list:
    """
    Extract GBP sold prices from eBay completed listings HTML.
    Looks for prices in the sold/completed results section.
    """
    # Match price patterns like £12.50, £120.00
    raw = re.findall(r'£([\d,]+\.?\d*)', html)
    prices = []
    for p in raw:
        try:
            val = float(p.replace(",", ""))
            # Filter out clearly wrong values
            if 1.0 <= val <= 5000.0:
                prices.append(val)
        except ValueError:
            continue
    return prices


def check_sold_value(item: dict) -> dict:
    """
    Search eBay UK completed/sold listings for the book title.
    Returns real transaction prices — more reliable than asking prices.

    Returns dict with:
        found          (bool)   — whether sold results were found
        lowest_sold    (float)  — lowest sold price
        highest_sold   (float)  — highest sold price
        median_sold    (float)  — median sold price
        confirmed_flip (bool)   — True if Vinted price < 1/3 of median sold
        multiple       (float)  — how many times more eBay sold vs Vinted price
        search_title   (str)    — what was searched
        source         (str)    — always "eBay sold"
    """
    default = {
        "found": False, "lowest_sold": 0, "highest_sold": 0,
        "median_sold": 0, "confirmed_flip": False,
        "multiple": 0, "search_title": "", "source": "eBay sold",
    }

    title = item.get("title", "")
    if not title:
        return default

    search_query = _clean_title(title)
    if not search_query:
        return default

    # Append antiquarian/Victorian terms to avoid modern reprints
    year_hint = item.get("year_hint")
    if year_hint and 1800 <= year_hint <= 1898:
        search_query = f"{search_query} {year_hint}"
    else:
        search_query = f"{search_query} antique victorian"

    params = {
        "_nkw":             search_query,
        "_sacat":           "29223",    # Antiquarian & Collectible Books category
        "LH_Sold":          "1",        # Sold listings only
        "LH_Complete":      "1",        # Completed listings
        "_sop":             "13",       # Sort by most recent
        "_ipg":             "60",       # 60 results
        "LH_ItemCondition": "3000|4000|5000",  # Used conditions
        "Year_Published":   "1800-1899", # eBay year filter where supported
    }

    try:
        resp = requests.get(
            EBAY_SEARCH, params=params,
            headers=headers, timeout=12
        )
        if not resp.ok:
            return default

        prices = _extract_sold_prices(resp.text)
        if not prices:
            return default

        prices.sort()
        # Remove outliers — ignore bottom 10% and top 10%
        trim = max(1, len(prices) // 10)
        if len(prices) > 4:
            prices = prices[trim:-trim]

        if not prices:
            return default

        lowest  = prices[0]
        highest = prices[-1]
        median  = prices[len(prices) // 2]

        vinted_price = float(item.get("price", 999))
        multiple     = round(median / vinted_price, 1) if vinted_price > 0 else 0
        confirmed    = vinted_price > 0 and (median / vinted_price) >= FLIP_THRESHOLD

        return {
            "found":          True,
            "lowest_sold":    lowest,
            "highest_sold":   highest,
            "median_sold":    median,
            "confirmed_flip": confirmed,
            "multiple":       multiple,
            "search_title":   search_query,
            "source":         "eBay sold",
        }

    except Exception as e:
        print(f"  [ebay] Lookup failed: {e}")
        return default