# activity_monitor.py — detects potentially undervalued Victorian listings
#                        by monitoring favourites accumulation rate
#
# Core insight: when a cheap listing is gaining favourites quickly, it means
# other buyers (often dealers) are recognising value the seller doesn't.
# Rate of accumulation is a stronger signal than raw count alone.
#
# Three alert triggers — any one fires:
#   1. RATE  — favourites/hour >= FAV_RATE_ALERT (sustained dealer interest)
#   2. SPIKE — favourites gained in one scan >= FAV_SPIKE_ALERT (sudden attention)
#   3. PRICE-ADJUSTED ABSOLUTE — total favourites exceeds a threshold that
#              scales with listing price (5 favs on a £3 book is extraordinary)
#
# Zero Anthropic API credits used — text-only Victorian check, Vinted API only.
# Listings expire after MAX_AGE_HOURS. Each listing alerts at most once.

import json
import os
import re
import requests
from datetime import datetime, timezone

WATCHED_FILE  = "watched_listings.json"
MAX_WATCHED   = 200    # cap to keep file lean
MAX_AGE_HOURS = 72     # stop watching after 3 days
PRICE_CEILING = 20.0   # above this, seller likely knows the value

# ── Alert thresholds ──────────────────────────────────────────────────────────
FAV_RATE_ALERT  = 1.5  # favourites/hour since listing first seen — sustained interest
FAV_SPIKE_ALERT = 4    # favourites gained in a single scan cycle — sudden spike


def _price_threshold(price: float) -> int:
    """
    Price-adjusted absolute favourites threshold.
    Cheaper listings need fewer favourites to signal undervaluation —
    a £3 book with 5 favourites is extraordinary; a £25 book with 5 is unremarkable.
    """
    if price < 5:  return 5
    if price < 15: return 7
    if price < 30: return 9
    return 12


VINTED_ITEM_API    = "https://www.vinted.co.uk/api/v2/items/{item_id}"
VICTORIAN_YEAR_MIN = 1800
VICTORIAN_YEAR_MAX = 1910

# Year regex — same logic as vinted.py, excludes catalogue suffixes like 1801-2C
_YEAR_RE = re.compile(r'(?<!\d)((?:1[7-9]|20)\d{2})(?!\d)(?!-\d*[A-Za-z])')


# ── Storage helpers ───────────────────────────────────────────────────────────

def _load() -> dict:
    if not os.path.exists(WATCHED_FILE):
        return {}
    try:
        with open(WATCHED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict):
    with open(WATCHED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── Victorian text check ──────────────────────────────────────────────────────

def is_victorian_by_text(item: dict) -> bool:
    """
    Text-only check — no image analysis, no API credits.
    Two explicit steps:

    Step 1 — Year scan
        Search title + description for any 4-digit year.
        If a year in 1800–1910 is found → True.

    Step 2 — Publisher scan (only if no Victorian year found)
        Search title + description for any publisher from PUBLISHER_SIGNALS.
        If found → True.

    Anything else → False.
    """
    combined = (
        (item.get("title") or "") + " " +
        (item.get("description") or "")
    ).lower()

    # Step 1: year scan
    years = [int(y) for y in _YEAR_RE.findall(combined)]
    if any(VICTORIAN_YEAR_MIN <= y <= VICTORIAN_YEAR_MAX for y in years):
        return True

    # Step 2: publisher scan
    from config import PUBLISHER_SIGNALS
    return any(pub in combined for pub in PUBLISHER_SIGNALS)


# ── Watchlist management ──────────────────────────────────────────────────────

def add_to_watchlist(item: dict):
    """
    Add a listing to watched_listings.json if it passes the Victorian text check.
    Called from main.py for every new listing, before hard_block runs.
    """
    if not is_victorian_by_text(item):
        return

    price = float(item.get("price", 999))
    if price > PRICE_CEILING:
        return

    item_id = str(item.get("id", ""))
    if not item_id:
        return

    watched = _load()
    if item_id in watched:
        return

    # Enforce cap — drop the oldest entry if at limit
    if len(watched) >= MAX_WATCHED:
        oldest_id = min(watched, key=lambda k: watched[k].get("added", ""))
        del watched[oldest_id]

    initial_favs = int(item.get("favourites", 0) or 0)
    watched[item_id] = {
        "title":            item.get("title", ""),
        "price":            price,
        "url":              item.get("url", f"https://www.vinted.co.uk/items/{item_id}"),
        "year_hint":        item.get("year_hint"),
        "seller":           item.get("seller", ""),
        "added":            datetime.now(tz=timezone.utc).isoformat(),
        "first_favourites": initial_favs,
        "last_favourites":  initial_favs,
        "peak_rate":        0.0,   # highest favs/hour seen — stored for alert context
        "last_checked":     datetime.now(tz=timezone.utc).isoformat(),
        "alerted":          False,
    }
    _save(watched)


# ── Vinted re-fetch ───────────────────────────────────────────────────────────

def _fetch_current_favourites(item_id: str, session) -> int | None:
    """
    Re-fetch a listing's current favourite count from Vinted's public API.
    Returns:
        int  — current favourite count
        None — listing gone (404 / sold / removed)
        -1   — temporary failure, retry next scan
    """
    url = VINTED_ITEM_API.format(item_id=item_id)
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code == 404:
            return None
        if not resp.ok:
            return -1
        data = resp.json()
        raw  = data.get("item", {})
        favs = raw.get("favourite_count") or raw.get("favorites_count") or 0
        return int(favs)
    except Exception:
        return -1


# ── Rate calculation ──────────────────────────────────────────────────────────

def _calc_rate(entry: dict, current_favs: int) -> float:
    """
    Favourites gained per hour since this listing was first added to the watchlist.
    Minimum window of 15 minutes to avoid inflated rates on brand-new entries.
    """
    hours = max(_hours_since(entry["added"]), 0.25)
    growth = max(current_favs - entry["first_favourites"], 0)
    return round(growth / hours, 2)


# ── Alert decision ────────────────────────────────────────────────────────────

def _should_alert(entry: dict, current_favs: int, scan_growth: int) -> tuple[bool, str]:
    """
    Returns (True, reason_string) if any undervaluation signal threshold is met.

    Three independent checks — any one is sufficient:
      RATE   — sustained accumulation rate above FAV_RATE_ALERT favs/hour
      SPIKE  — sudden jump of FAV_SPIKE_ALERT or more in a single scan
      VOLUME — total favourites exceeds the price-adjusted absolute threshold
    """
    rate  = _calc_rate(entry, current_favs)
    price = float(entry.get("price", 99))

    if rate >= FAV_RATE_ALERT and (current_favs - entry["first_favourites"]) >= 2:
        return True, f"rate {rate:.1f}/hr"

    if scan_growth >= FAV_SPIKE_ALERT:
        return True, f"spike +{scan_growth} this scan"

    if current_favs >= _price_threshold(price):
        return True, f"{current_favs} favourites for £{price:.0f} listing"

    return False, ""


# ── Telegram alert ────────────────────────────────────────────────────────────

def _send_activity_alert(
    item_id: str,
    entry: dict,
    current_favs: int,
    scan_growth: int,
    trigger_reason: str,
    telegram_token: str,
    chat_id: str,
):
    """
    Fire a Telegram activity alert framed around undervaluation.
    Shows rate, total favourites, and listing age so the context is clear.
    """
    rate      = _calc_rate(entry, current_favs)
    year_str  = f" · {entry['year_hint']}" if entry.get("year_hint") else ""
    age_str   = _format_age(entry["added"])
    total_growth = current_favs - entry["first_favourites"]

    # Build the favourites line — rate is the headline number
    if rate >= FAV_RATE_ALERT:
        fav_line = f"❤️ {current_favs} favourites · <b>{rate:.1f}/hr</b> · +{total_growth} since listed"
    elif scan_growth >= FAV_SPIKE_ALERT:
        fav_line = f"❤️ {current_favs} favourites · <b>+{scan_growth} this scan</b> · {rate:.1f}/hr"
    else:
        fav_line = f"❤️ {current_favs} favourites · {rate:.1f}/hr · +{total_growth} since listed"

    message = (
        f"🔥 <b>High Activity — possibly undervalued</b>\n"
        f"\n"
        f"📚 <b>{entry['title']}</b>\n"
        f"💰 £{entry['price']:.2f}{year_str}\n"
        f"{fav_line}\n"
        f"🕐 Listed {age_str}\n"
        f"👤 {entry.get('seller', '—')}\n"
        f"\n"
        f"<i>Trigger: {trigger_reason}</i>\n"
        f"<i>Text signals only — no image analysis yet.</i>\n"
        f"\n"
        f"🔗 {entry['url']}"
    )

    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    try:
        inline_keyboard = {"inline_keyboard": [[
            {"text": "❌ Not a buy", "callback_data": f"dismiss_activity|{item_id}"},
        ]]}
        requests.post(url, data={
            "chat_id":      chat_id,
            "text":         message,
            "parse_mode":   "HTML",
            "reply_markup": json.dumps(inline_keyboard),
        }, timeout=10)
        print(
            f"  🔥 Activity alert: {entry['title'][:50]} "
            f"({current_favs} favs · {rate:.1f}/hr · {trigger_reason})"
        )
    except Exception as e:
        print(f"  [activity] Alert send failed: {e}")


# ── Age / time helpers ────────────────────────────────────────────────────────

def _hours_since(iso_str: str) -> float:
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(tz=timezone.utc) - dt).total_seconds() / 3600
    except Exception:
        return 9999.0


def _format_age(iso_str: str) -> str:
    hours = _hours_since(iso_str)
    if hours < 1:
        return f"{int(hours * 60)}m ago"
    if hours < 24:
        h = int(hours)
        m = int((hours - h) * 60)
        return f"{h}h {m}m ago" if m else f"{h}h ago"
    return f"{int(hours / 24)}d ago"


# ── Main check — called once per scan ────────────────────────────────────────

def check_watched_listings(session, telegram_token: str, chat_id: str):
    """
    Re-fetch favourites for all watched listings and alert on undervaluation signals.
    Called once at the start of each scan from main.py. Zero API credits.
    """
    watched = _load()
    if not watched:
        return

    to_remove = []
    changed   = False

    for item_id, entry in list(watched.items()):

        # Expire old listings
        if _hours_since(entry["added"]) > MAX_AGE_HOURS:
            to_remove.append(item_id)
            continue

        # Already alerted — keep until expiry to prevent re-adding, skip re-check
        if entry.get("alerted"):
            continue

        current_favs = _fetch_current_favourites(item_id, session)

        if current_favs is None:
            # Listing gone (sold or removed)
            to_remove.append(item_id)
            changed = True
            continue

        if current_favs < 0:
            # Temporary Vinted API failure — retry next scan
            continue

        prev_favs   = int(entry.get("last_favourites", 0))
        scan_growth = current_favs - prev_favs

        # Update stored state
        entry["last_favourites"] = current_favs
        entry["last_checked"]    = datetime.now(tz=timezone.utc).isoformat()
        rate = _calc_rate(entry, current_favs)
        if rate > float(entry.get("peak_rate", 0)):
            entry["peak_rate"] = rate
        changed = True

        alert, reason = _should_alert(entry, current_favs, scan_growth)

        if alert:
            _send_activity_alert(
                item_id, entry, current_favs, scan_growth,
                reason, telegram_token, chat_id,
            )
            entry["alerted"] = True

    for item_id in to_remove:
        del watched[item_id]

    if changed:
        _save(watched)

    active  = len([e for e in watched.values() if not e.get("alerted")])
    alerted = len([e for e in watched.values() if e.get("alerted")])
    if watched:
        print(f"  [activity] {active} watching · {alerted} alerted · {len(to_remove)} expired")