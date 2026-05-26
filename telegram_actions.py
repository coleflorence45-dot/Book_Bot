# telegram_actions.py — handles quick-action button callbacks from Telegram
#
# Run this alongside main.py in a separate terminal:
#   python telegram_actions.py
#
# When you tap ✅ Bought or ❌ Skip on an alert, this script receives the
# callback and logs it to book_history.json automatically.
#
# Callback data format (max 64 bytes):
#   bought|{item_id}|{price}|{short_title}
#   skip|{item_id}

import json
import os
import time
import requests
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

HISTORY_FILE         = "book_history.json"
OFFSET_FILE          = "telegram_offset.txt"
PENDING_SELLERS_FILE = "pending_sellers.json"
API_BASE             = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

VINTED_ITEM_URL = "https://www.vinted.co.uk/items/{item_id}"
VINTED_ITEM_API = "https://www.vinted.co.uk/api/v2/items/{item_id}"


def _add_pending_seller(item_id: str):
    """
    Read pending_sellers.json and add the seller to watchlist if present.
    Called only when the user taps ✅ Bought — not on every BUY alert.
    """
    try:
        if not os.path.exists(PENDING_SELLERS_FILE):
            return
        with open(PENDING_SELLERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        seller_info = data.get(str(item_id))
        if not seller_info:
            return
        from seller_watchlist import add_seller
        # Build a minimal item dict that add_seller expects
        add_seller({
            "seller_id": seller_info.get("seller_id", ""),
            "seller":    seller_info.get("seller", "unknown"),
            "title":     seller_info.get("title", ""),
        })
    except Exception as e:
        print(f"  [actions] Could not add seller to watchlist: {e}")


def load_offset() -> int:
    if os.path.exists(OFFSET_FILE):
        try:
            with open(OFFSET_FILE) as f:
                return int(f.read().strip())
        except Exception:
            pass
    return 0


def save_offset(offset: int):
    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))


def answer_callback(callback_id: str, text: str):
    """Acknowledge the button tap so Telegram removes the loading spinner.
    Must be called within ~5 seconds of the tap — after that Telegram times out.
    Uses form data (data=) not JSON — more reliable across Bot API versions."""
    try:
        resp = requests.post(f"{API_BASE}/answerCallbackQuery", data={
            "callback_query_id": str(callback_id),
            "text":              text,
            "show_alert":        "false",
        }, timeout=8)
        if not resp.ok:
            print(f"  [actions] answerCallbackQuery failed: {resp.status_code} {resp.text[:120]}")
    except Exception as e:
        print(f"  [actions] answerCallbackQuery error: {e}")


def edit_message_text(chat_id, message_id: int, new_text: str):
    """Update the alert message after action is taken."""
    requests.post(f"{API_BASE}/editMessageText", json={
        "chat_id":    chat_id,
        "message_id": message_id,
        "text":       new_text,
        "parse_mode": "HTML",
    }, timeout=10)


def _fetch_listing_photo(item_id: str) -> str:
    """
    Try to fetch the first photo URL from the Vinted API for this item.
    Returns base64-encoded photo string or empty string on failure.
    """
    try:
        url  = VINTED_ITEM_API.format(item_id=item_id)
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
        if not resp.ok:
            return ""
        data      = resp.json()
        photos    = data.get("item", {}).get("photos") or []
        photo_url = photos[0].get("url", "") if photos else ""
        if not photo_url:
            return ""
        import base64 as _b64
        photo_resp = requests.get(photo_url, timeout=10)
        if not photo_resp.ok:
            return ""
        b64        = _b64.standard_b64encode(photo_resp.content).decode("utf-8")
        media_type = photo_resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
        print(f"  📸 Photo fetched from Vinted for history")
        return f"data:{media_type};base64,{b64}"
    except Exception as e:
        print(f"  [actions] Could not fetch photo: {e}")
        return ""


def log_bought(data: dict):
    """Auto-log a bought book to book_history.json."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = {"books": []}
    else:
        history = {"books": []}

    item_id = data.get("item_id", "")

    # Reconstruct the Vinted listing URL from item_id
    item_url = VINTED_ITEM_URL.format(item_id=item_id) if item_id else ""

    # Try to fetch listing photo from Vinted API
    photos = []
    if item_id:
        photo_b64 = _fetch_listing_photo(item_id)
        if photo_b64:
            photos = [photo_b64]

    entry = {
        "vinted_item_id": item_id,
        "title":          data.get("title", ""),
        "bought_price":   float(data.get("price", 0)),
        "bought_date":    datetime.now().strftime("%Y-%m-%d"),
        "sold_price":     None,
        "sold_date":      None,
        "sold_platform":  None,
        "profit":         None,
        "notes":          "Auto-logged via Telegram button",
        "url":            item_url,
        "photos":         photos,
    }

    history["books"].append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Logged to history: {entry['title']} @ £{entry['bought_price']}")


def log_sold(sold_price: float, chat_id) -> str:
    """
    Mark the most recently bought (unsold) book as sold at the given price.
    Updates book_history.json and returns a confirmation string.
    """
    if not os.path.exists(HISTORY_FILE):
        return "❌ No history file found."
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception:
        return "❌ Could not read history file."

    books = history.get("books", [])
    # Find the most recent unsold entry (sold_price is None)
    target = None
    for book in reversed(books):
        if not book.get("_example") and book.get("sold_price") is None and book.get("bought_price"):
            target = book
            break

    if not target:
        return "❌ No unsold books found in history."

    bought_price  = float(target.get("bought_price", 0))
    profit        = round(sold_price * 0.95 - bought_price, 2)  # ~5% Vinted fee
    target["sold_price"]    = sold_price
    target["sold_date"]     = datetime.now().strftime("%Y-%m-%d")
    target["sold_platform"] = "Vinted"
    target["profit"]        = profit

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    title = target.get("title", "Unknown")[:40]
    return (
        f"✅ <b>Sold logged!</b>\n"
        f"📚 {title}\n"
        f"💰 Bought £{bought_price:.2f} → Sold £{sold_price:.2f}\n"
        f"📈 Profit: £{profit:.2f} (after ~5% fees)"
    )


def parse_callback_data(raw: str) -> dict:
    """
    Callback data format: action|item_id|price|short_title
                    or:   skip|item_id
    """
    try:
        parts = raw.split("|", 3)
        return {
            "action":  parts[0] if len(parts) > 0 else "",
            "item_id": parts[1] if len(parts) > 1 else "",
            "price":   parts[2] if len(parts) > 2 else "0",
            "title":   parts[3] if len(parts) > 3 else "",
        }
    except Exception:
        return {}


def poll():
    """Long-poll Telegram for callback query updates."""
    print("🎛️  Telegram action handler running — waiting for button taps...")
    offset = load_offset()

    while True:
        try:
            resp = requests.get(f"{API_BASE}/getUpdates", params={
                "offset":          offset,
                "timeout":         30,
                "allowed_updates": ["callback_query", "message"],
            }, timeout=40)

            if not resp.ok:
                time.sleep(5)
                continue

            updates = resp.json().get("result", [])

            for update in updates:
                offset = update["update_id"] + 1
                save_offset(offset)

                cq = update.get("callback_query")
                msg = update.get("message")

                # ── /sold command ─────────────────────────────────────────────
                # Usage: /sold 45  or  /sold 45.50
                # Marks the most recent unsold book as sold at that price.
                if msg and msg.get("text", "").startswith("/sold"):
                    chat_id = msg["chat"]["id"]
                    parts   = msg["text"].strip().split()
                    if len(parts) >= 2:
                        try:
                            sold_price = float(parts[1].replace("£", ""))
                            reply      = log_sold(sold_price, chat_id)
                        except ValueError:
                            reply = "❌ Usage: /sold 45.00"
                    else:
                        reply = "❌ Usage: /sold 45.00"
                    requests.post(f"{API_BASE}/sendMessage", json={
                        "chat_id":    chat_id,
                        "text":       reply,
                        "parse_mode": "HTML",
                    }, timeout=10)
                    continue

                if not cq:
                    continue

                callback_id = cq["id"]
                chat_id     = cq["message"]["chat"]["id"]
                message_id  = cq["message"]["message_id"]
                raw_data    = cq.get("data", "")
                data        = parse_callback_data(raw_data)
                action      = data.get("action", "")

                if action == "bought":
                    log_bought(data)
                    _add_pending_seller(data.get("item_id", ""))
                    answer_callback(callback_id, "✅ Logged as bought!")
                    edit_message_text(
                        chat_id, message_id,
                        f"✅ <b>BOUGHT</b> — {data.get('title', '')} @ £{data.get('price', '')}\n"
                        f"Logged to book_history.json — remember to update when sold."
                    )
                    print(f"  ✅ BOUGHT tapped: {data.get('title')}")

                elif action == "skip":
                    # Answer FIRST — clears the loading spinner immediately
                    answer_callback(callback_id, "❌ Skipped")
                    try:
                        del_resp = requests.post(f"{API_BASE}/deleteMessage", json={
                            "chat_id":    chat_id,
                            "message_id": message_id,
                        }, timeout=10)
                        if not del_resp.ok:
                            # Delete failed (e.g. message too old) — edit instead
                            edit_message_text(chat_id, message_id, "❌ Skipped")
                    except Exception as e:
                        print(f"  [actions] deleteMessage error: {e}")
                    print(f"  ❌ SKIP tapped: {data.get('item_id', '')}")

                elif action == "dismiss_activity":
                    answer_callback(callback_id, "🗑️ Dismissed")
                    try:
                        del_resp = requests.post(f"{API_BASE}/deleteMessage", json={
                            "chat_id":    chat_id,
                            "message_id": message_id,
                        }, timeout=10)
                        if not del_resp.ok:
                            edit_message_text(chat_id, message_id, "🗑️ Dismissed")
                    except Exception as e:
                        print(f"  [actions] deleteMessage error: {e}")
                    print(f"  🗑️  Activity alert dismissed: {data.get('item_id', '')}")

        except KeyboardInterrupt:
            print("\n⛔ Action handler stopped.")
            break
        except Exception as e:
            print(f"  [actions] Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    poll()