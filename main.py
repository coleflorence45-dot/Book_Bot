# main.py — Vinted Books Bot
# Pipeline: keyword search + seller watchlist → hard block → score → image analysis → alert

import time
import random
import json
import re
import os
from datetime import datetime

from config import (
    SEARCH_KEYWORDS, MIN_PRICE, MAX_PRICE,
    CHECK_INTERVAL_MINUTES_MIN, CHECK_INTERVAL_MINUTES_MAX,
    MIN_SCORE, GOOD_CONDITIONS,
    PRIORITY_GENRE_NATURAL_HISTORY, PRIORITY_GENRE_ASTRONOMY, PRIORITY_GENRE_OCCULT,
)
from vinted            import fetch_listings, fetch_seller_listings, format_item, get_session_cookie
from scorer            import score_item, hard_block, passes_condition_filter
from image_analyser    import analyse_image
from telegram_bot      import send_alert, send_image
from tracker           import load_seen, save_seen, is_new, mark_seen
from seller_watchlist  import get_watched_sellers, record_404, record_success
from skip_logger       import log_skip
from keyword_learner   import learn_from_alert, get_suggestions
from abebooks_checker  import check_market_value
from ebay_checker      import check_sold_value
from image_cache       import get_cached_verdict, cache_verdict
from pricing           import calculate_sell_price
from book_identifier   import should_identify, identify_book, enrich_item
from activity_monitor  import add_to_watchlist, check_watched_listings

ALERT_LOG_FILE          = "alert_log.json"
PENDING_SELLERS_FILE    = "pending_sellers.json"


def _store_pending_seller(item: dict):
    """
    Save seller info keyed by item_id so telegram_actions.py can add the seller
    to the watchlist only if the user actually taps ✅ Bought.
    """
    try:
        data = {}
        if os.path.exists(PENDING_SELLERS_FILE):
            with open(PENDING_SELLERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        data[str(item.get("id", ""))] = {
            "seller_id":  str(item.get("seller_id", "")),
            "seller":     item.get("seller", "unknown"),
            "title":      item.get("title", ""),
        }
        with open(PENDING_SELLERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"  [seller] Could not store pending seller: {e}")


def log_alert(item: dict, verdict: dict):
    """Append every BUY or UNSURE alert to alert_log.json for pattern analysis."""
    now   = datetime.now()
    entry = {
        "timestamp":    now.strftime("%Y-%m-%d %H:%M"),
        "date":         now.strftime("%Y-%m-%d"),
        "time":         now.strftime("%H:%M"),
        "day":          now.strftime("%A"),
        "hour":         now.hour,
        "action":       verdict.get("action"),
        "title":        item.get("title"),
        "price":        item.get("price"),
        "score":        item.get("score"),
        "url":          item.get("url"),
        "image_reason": verdict.get("reason"),
        "signals":      item.get("signals", []),
    }
    if os.path.exists(ALERT_LOG_FILE):
        try:
            with open(ALERT_LOG_FILE, "r", encoding="utf-8") as f:
                log = json.load(f)
        except Exception:
            log = {"alerts": []}
    else:
        log = {"alerts": []}
    log["alerts"].append(entry)
    with open(ALERT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def send_weekly_digest():
    """Every Sunday at 8pm, send a summary + keyword suggestions to Telegram."""
    now = datetime.now()
    if now.weekday() != 6 or now.hour != 20:
        return
    digest_flag = "weekly_digest_sent.txt"
    today = now.strftime("%Y-%m-%d")
    if os.path.exists(digest_flag):
        with open(digest_flag) as f:
            if f.read().strip() == today:
                return

    suggestions = get_suggestions(min_count=2)
    watched     = get_watched_sellers()

    lines = [
        "📚 <b>Book Bot — Weekly Digest</b>",
        "",
        f"👁️ Sellers on watchlist: <b>{len(watched)}</b>",
    ]
    if suggestions:
        lines += ["", "<b>Words appearing in BUY titles — consider adding as keywords:</b>"]
        for word, count in suggestions[:8]:
            lines.append(f"  • {word} ({count}x)")
    else:
        lines.append("\nNo keyword suggestions yet — more BUY alerts needed.")

    import requests as _req
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    url     = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": "\n".join(lines), "parse_mode": "HTML"}
    try:
        _req.post(url, data=payload, timeout=10)
        with open(digest_flag, "w") as f:
            f.write(today)
        print("📬 Weekly digest sent to Telegram")
    except Exception as e:
        print(f"  [digest] Error: {e}")


def process_items(items: list, seen_ids: set, new_seen: set, stats: dict):
    """Run the full filtering pipeline on a list of raw Vinted items."""
    for raw_item in items:
        item = format_item(raw_item)
        stats["total"] += 1

        if not is_new(item["id"], new_seen):
            stats["already_seen"] += 1
            continue
        new_seen.add(str(item["id"]))
        mark_seen(item["id"])  # Persist immediately — prevents re-alert if bot restarts mid-scan

        # Activity monitor — add to watchlist before hard_block so we catch
        # Victorian-year listings that might otherwise be filtered out
        add_to_watchlist(item)

        if item["price"] < MIN_PRICE:
            stats["hard_blocked"] += 1
            continue

        blocked, reason = hard_block(item)
        if blocked:
            print(f"  🚫 Hard block ({reason}): {item['title']}")
            stats["hard_blocked"] += 1
            continue

        if not passes_condition_filter(item, GOOD_CONDITIONS):
            print(f"  ⛔ Condition skip [{item['condition']}]: {item['title']}")
            stats["hard_blocked"] += 1
            continue

        score_item(item)

        # Dynamic price ceiling — let higher-scored listings go above £20
        if item["price"] > MAX_PRICE:
            stats["hard_blocked"] += 1
            continue

        # ── Book identifier ───────────────────────────────────────────────────
        # Fires in three cases:
        # 1. Score 4-5 + vague + age hint — borderline listing worth checking
        # 2. Score 8+ + no Victorian year — high confidence, investigate photo
        # 3. Priority genre match + no year — e.g. "The Moths of the British Isles"
        #    with no date on title page but clearly worth investigating
        year               = item.get("year_hint")
        has_victorian_year = year and 1800 <= int(year) <= 1898
        is_vague           = should_identify(item)

        AGE_HINT_SIGNALS = [
            "gilt", "leather", "illustrated", "cloth", "antique",
            "decorative", "victorian", "hardback", "hardcover",
            "embossed", "engraved", "plates", "coloured",
            "original edition", "first edition", "1st edition",
        ]
        title_lower  = (item.get("title") or "").lower()
        has_age_hint = any(s in title_lower for s in AGE_HINT_SIGNALS)

        combined_text     = (item.get("title", "") + " " + (item.get("description") or "")).lower()
        is_priority_genre = (
            any(g.lower() in combined_text for g in PRIORITY_GENRE_NATURAL_HISTORY) or
            any(g.lower() in combined_text for g in PRIORITY_GENRE_ASTRONOMY) or
            any(g.lower() in combined_text for g in PRIORITY_GENRE_OCCULT)
        )

        STRONG_BOOK_TITLE_WORDS = {
            "book", "books", "hardback", "hardcover", "paperback",
            "volume", "edition", "illustrated", "history", "guide",
            "atlas", "manual", "treatise", "memoir", "voyage", "travels",
        }
        title_words     = set(re.findall(r'\b\w+\b', title_lower))
        looks_like_book = bool(title_words & STRONG_BOOK_TITLE_WORDS)

        is_borderline    = 4 <= item["score"] <= 5 and is_vague and has_age_hint
        is_high_no_year  = item["score"] >= 7 and not has_victorian_year and has_age_hint and looks_like_book
        is_genre_no_year = is_priority_genre and not has_victorian_year and item["score"] >= MIN_SCORE and has_age_hint and looks_like_book

        if is_borderline or is_high_no_year or is_genre_no_year:
            if is_high_no_year:
                print(f"  🔍 High score ({item['score']}) but no year — reading photo: {item['title']}")
            elif is_genre_no_year:
                print(f"  🔍 Priority genre but no year — reading photo: {item['title']}")
            else:
                print(f"  🔍 Borderline vague — identifying from photo: {item['title']}")

            identified     = identify_book(item)
            extracted_year      = identified.get("year") if identified else None
            extracted_publisher = (identified.get("publisher") or "").lower() if identified else ""
            year_ceiling        = 1910 if is_priority_genre else 1900
            is_victorian        = extracted_year and 1800 <= int(extracted_year) <= year_ceiling

            # Check if extracted publisher is one of our known quality publishers
            # Frederick Warne, Macmillan etc. only published in a specific era
            from config import PUBLISHER_SIGNALS
            has_quality_publisher = any(
                pub.lower() in extracted_publisher
                for pub in PUBLISHER_SIGNALS
                if len(pub) > 4  # avoid short false matches
            )

            if identified and identified.get("confidence") != "low" and (is_victorian or has_quality_publisher):
                item = enrich_item(item, identified)
                item["_identifier_enriched"] = True
                stats["input_tokens"]  += identified.get("_tokens_in", 0)
                stats["output_tokens"] += identified.get("_tokens_out", 0)
                item["signals"] = []
                item["score"]   = 0
                score_item(item)
                blocked, reason = hard_block(item)
                if blocked:
                    print(f"  🚫 Hard block after ID ({reason}): {item['title']}")
                    stats["hard_blocked"] += 1
                    continue
                if has_quality_publisher and not is_victorian:
                    print(f"  📖 Quality publisher found ({extracted_publisher}) — proceeding without year")
                    # Flag so the year gate below knows to bypass
                    item["_publisher_confirmed"] = True
            elif extracted_year and int(extracted_year) > year_ceiling:
                print(f"  🚫 Identifier found post-cutoff year ({extracted_year}) — skipping")
                stats["hard_blocked"] += 1
                continue
            elif (is_high_no_year or is_genre_no_year) and not is_victorian and not has_quality_publisher:
                print(f"  ⏭️  No Victorian year or quality publisher found in photo — skipping: {item['title']}")
                stats["no_signals"] += 1
                continue

        if item["score"] < MIN_SCORE:
            print(f"  ⚪ Low score ({item['score']}): {item['title']}")
            stats["low_score"] += 1
            continue

        print(f"  🟡 Score {item['score']} — checking signals: {item['title']}")

        # ── Victorian year mandatory (or quality publisher confirmed) ──────────
        year               = item.get("year_hint")
        year_ceiling       = 1910 if is_priority_genre else 1900
        has_victorian_year = year and 1800 <= int(year) <= year_ceiling
        publisher_confirmed = item.get("_publisher_confirmed", False)

        if not has_victorian_year and not publisher_confirmed:
            print(f"  ⏭️  No confirmed year or publisher — skipping: {item['title']}")
            stats["no_signals"] += 1
            continue

        hard_positive_signals = [s for s in item["signals"] if any(
            marker in s for marker in [
                "Sweet spot year", "Publisher:",
                "Colour", "Fold", "Lithograph", "Hand-Coloured",
                "Chromolithograph", "🏛️", "🎨", "📅",
            ]
        )]

        # Hard signal threshold:
        # - Confirmed Victorian year: 1 required — the year IS the evidence.
        #   "African Hunting 1852", "Antique books 1885" should not be blocked here.
        # - No year, identifier confirmed publisher: 2 required
        # - No year, identifier ran but found nothing definitive: 3 required
        is_enriched_no_pub = item.get("_identifier_enriched") and not item.get("_publisher_confirmed")
        if has_victorian_year:
            min_hard = 1
        elif is_enriched_no_pub:
            min_hard = 3
        else:
            min_hard = 2
        if len(hard_positive_signals) < min_hard:
            print(f"  ⏭️  Skipping image — only {len(hard_positive_signals)} hard signal(s): {item['title']}")
            stats["no_signals"] += 1
            continue

        print(f"  📸 Image analysis: {item['title']}")

        # Check cache first — avoid re-paying for previously analysed items
        cached = get_cached_verdict(str(item["id"]))
        if cached:
            print(f"  💾 Cached result ({cached['action']}): {item['title']}")
            verdict = dict(cached)
            verdict["input_tokens"]  = 0
            verdict["output_tokens"] = 0
        else:
            verdict = analyse_image(item["photo"], item.get("photo_urls", []))
            cache_verdict(str(item["id"]), verdict)

        item["image_verdict"] = verdict
        stats["input_tokens"]  += verdict.get("input_tokens", 0)
        stats["output_tokens"] += verdict.get("output_tokens", 0)

        if verdict["action"] == "SKIP":
            log_skip(item, verdict)
            print(f"  🔴 Image SKIP: {item['title']} — {verdict['reason']}")
            stats["image_skip"] += 1
            continue

        print(f"  ✅ ALERT [{verdict['action']}] score={item['score']}: {item['title']} — £{item['price']:.2f}")
        stats["alerts"] += 1

        if verdict["action"] == "BUY":
            stats["buy"] += 1
            learn_from_alert(item)
            # Store seller info for watchlist — only added when user taps ✅ Bought
            _store_pending_seller(item)
            # Market value cross-checks — AbeBooks (asking) + eBay (sold)
            abebooks = check_market_value(item)
            ebay     = check_sold_value(item)
            item["market_abebooks"] = abebooks
            item["market_ebay"]     = ebay
            if abebooks.get("confirmed_flip"):
                print(f"  🔥 AbeBooks CONFIRMED FLIP — from £{abebooks['lowest_price']} ({abebooks['multiple']}x)")
            if ebay.get("confirmed_flip"):
                print(f"  🔥 eBay CONFIRMED FLIP — median sold £{ebay['median_sold']} ({ebay['multiple']}x)")
            # Recommended sell price
            pricing = calculate_sell_price(
                buy_price = float(item.get("price", 0)),
                ebay      = ebay,
                abebooks  = abebooks,
                score     = item.get("score", 0),
            )
            item["pricing"] = pricing
            print(f"  💰 Recommended sell: £{pricing['recommended_price']:.0f} (est. profit £{pricing['estimated_profit']:.0f})")
        else:
            stats["unsure"] += 1
            item["market_abebooks"] = {}
            item["market_ebay"]     = {}
            item["pricing"]         = {}

        log_alert(item, verdict)
        send_alert(item)
        if item["photo"]:
            send_image(item["photo"])


def check_vinted():
    scan_start = time.time()
    print(f"🔍 Scanning Vinted for Victorian books... ({datetime.now().strftime('%H:%M')})")
    seen_ids = load_seen()
    new_seen = set(seen_ids)

    stats = {
        "total": 0, "already_seen": 0, "hard_blocked": 0,
        "low_score": 0, "no_signals": 0, "image_skip": 0,
        "alerts": 0, "buy": 0, "unsure": 0,
        "input_tokens": 0, "output_tokens": 0,
    }

    # ── Activity monitor — check favourites growth on watched listings ────────
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    from vinted import session as vinted_session
    check_watched_listings(vinted_session, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

    # ── Keyword searches ──────────────────────────────────────────────────────
    for keyword in SEARCH_KEYWORDS:
        items = fetch_listings(keyword, MAX_PRICE)
        time.sleep(random.uniform(5.0, 10.0))
        process_items(items, seen_ids, new_seen, stats)

    # ── Seller watchlist ──────────────────────────────────────────────────────
    watched = get_watched_sellers()
    if watched:
        print(f"\n  👁️  Checking {len(watched)} watched seller(s)...")
        for user_id, username in watched:
            items = fetch_seller_listings(user_id, 30.00)
            if items is None or (isinstance(items, list) and len(items) == 0):
                # fetch_seller_listings returns [] on 404 — check HTTP status
                # by trying once more and checking for removal
                removed = record_404(user_id)
                if not removed:
                    print(f"  [@{username}] 0 listing(s)")
            else:
                record_success(user_id)
                print(f"  [@{username}] {len(items)} listing(s)")
                time.sleep(random.uniform(5.0, 10.0))
                process_items(items, seen_ids, new_seen, stats)

    save_seen(new_seen)

    # ── Scan summary ──────────────────────────────────────────────────────────
    new_listings = stats["total"] - stats["already_seen"]
    input_cost   = (stats["input_tokens"]  / 1_000_000) * 3.00
    output_cost  = (stats["output_tokens"] / 1_000_000) * 15.00
    total_cost   = input_cost + output_cost
    cost_str     = f"${total_cost:.4f}" if total_cost > 0 else "$0.00"
    token_str    = f"{stats['input_tokens']:,} in / {stats['output_tokens']:,} out" if stats["input_tokens"] > 0 else "none"

    scan_secs = int(time.time() - scan_start)
    scan_mins, scan_s = divmod(scan_secs, 60)

    print(f"""
━━━ Scan Summary ━━━
⏱️  Scan duration:          {scan_mins}m {scan_s:02d}s
📋 Total listings seen:     {stats['total']}
👁️  Already seen (skipped):  {stats['already_seen']}
🆕 New listings checked:    {new_listings}
🚫 Hard blocked:            {stats['hard_blocked']}
⚪ Low score:               {stats['low_score']}
⏭️  No hard signals:         {stats['no_signals']}
🔴 Image SKIP:              {stats['image_skip']}
✅ Alerts fired:            {stats['alerts']} (🟢 BUY: {stats['buy']} · 🟡 UNSURE: {stats['unsure']})
💳 API tokens used:         {token_str}
💰 Estimated API cost:      {cost_str}
━━━━━━━━━━━━━━━━━━━━
""")
    send_weekly_digest()


import threading


def _start_telegram_actions():
    """Run the Telegram callback handler in a background daemon thread."""
    try:
        from telegram_actions import poll
        t = threading.Thread(target=poll, daemon=True, name="TelegramActions")
        t.start()
        print("🎛️  Telegram action handler started (background thread)")
    except Exception as e:
        print(f"  [actions] Could not start background handler: {e}")


# ── Entry point ───────────────────────────────────────────────────────────────
get_session_cookie()
_start_telegram_actions()

try:
    check_vinted()
except KeyboardInterrupt:
    print("\n⛔ Stopped.")
    exit(0)

while True:
    try:
        wait = random.randint(CHECK_INTERVAL_MINUTES_MIN, CHECK_INTERVAL_MINUTES_MAX)
        next_scan_time = datetime.fromtimestamp(time.time() + wait * 60).strftime("%H:%M")
        print(f"⏳ Next scan in {wait} minutes (at {next_scan_time})...\n")

        # Live countdown
        total_seconds = wait * 60
        while total_seconds > 0:
            mins, secs = divmod(total_seconds, 60)
            print(f"\r⏱️  {mins:02d}:{secs:02d} until next scan", end="", flush=True)
            time.sleep(1)
            total_seconds -= 1
        print("\r" + " " * 35 + "\r", end="", flush=True)

        check_vinted()
    except KeyboardInterrupt:
        print("\n⛔ Bot stopped by user.")
        exit(0)