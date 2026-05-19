# main.py — Vinted Books Bot
# Tuned for Victorian illustrated firsts, 1860–1898
#
# Pipeline per listing:
#   1. Fetch by keyword (vinted.py)
#   2. Skip already-seen IDs (tracker.py)
#   3. Price floor/ceiling check
#   4. Hard block: ex-library, post-1900, detached boards, missing plates (scorer.py)
#   5. Condition filter (scorer.py)
#   6. Score for age/publisher/illustration signals (scorer.py)
#   7. Skip if score < MIN_SCORE  ← avoids wasting image API calls
#   8. Claude Vision image analysis (image_analyser.py)
#   9. Skip if image SKIP + low score
#  10. Fire Telegram alert (telegram_bot.py)

import schedule
import time

from config import (
    SEARCH_KEYWORDS, MIN_PRICE, MAX_PRICE,
    CHECK_INTERVAL_MINUTES, MIN_SCORE, GOOD_CONDITIONS,
)
from vinted         import fetch_listings, format_item, get_session_cookie
from scorer         import score_item, hard_block, passes_condition_filter
from image_analyser import analyse_image
from telegram_bot   import send_alert, send_image
from tracker        import load_seen, save_seen, is_new


def check_vinted():
    print("🔍 Scanning Vinted for Victorian books...")
    seen_ids = load_seen()
    new_seen = set(seen_ids)

    for keyword in SEARCH_KEYWORDS:
        items = fetch_listings(keyword, MAX_PRICE)

        for raw_item in items:
            item = format_item(raw_item)

            # ── Already seen ──────────────────────────────────────────────────
            if not is_new(item["id"], new_seen):
                continue
            new_seen.add(str(item["id"]))

            # ── Price floor ───────────────────────────────────────────────────
            if item["price"] < MIN_PRICE:
                continue

            # ── Hard block (walk-away rules) ──────────────────────────────────
            blocked, reason = hard_block(item)
            if blocked:
                print(f"  🚫 Hard block ({reason}): {item['title']}")
                continue

            # ── Condition filter ──────────────────────────────────────────────
            if not passes_condition_filter(item, GOOD_CONDITIONS):
                print(f"  ⛔ Condition skip [{item['condition']}]: {item['title']}")
                continue

            # ── Score ─────────────────────────────────────────────────────────
            score_item(item)
            if item["score"] < MIN_SCORE:
                print(f"  ⚪ Low score ({item['score']}): {item['title']}")
                continue

            print(f"  🟡 Score {item['score']} — image analysis: {item['title']}")

            # ── Image analysis ────────────────────────────────────────────────
            verdict = analyse_image(item["photo"])
            item["image_verdict"] = verdict

            # Image SKIP is always respected — the visual layer is the final check
            if verdict["action"] == "SKIP":
                print(f"  🔴 Image SKIP: {item['title']} — {verdict['reason']}")
                continue

            # ── Alert ─────────────────────────────────────────────────────────
            print(f"  ✅ ALERT [{verdict['action']}] score={item['score']}: {item['title']} — £{item['price']:.2f}")
            send_alert(item)
            if item["photo"]:
                send_image(item["photo"])

    save_seen(new_seen)
    print("✅ Scan complete.\n")


get_session_cookie()

try:
    check_vinted()
except KeyboardInterrupt:
    print("\n⛔ Stopped.")
    exit(0)

schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_vinted)

while True:
    try:
        schedule.run_pending()
        time.sleep(20)
    except KeyboardInterrupt:
        print("\n⛔ Bot stopped by user.")
        exit(0)