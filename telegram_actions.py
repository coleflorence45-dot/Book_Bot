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

HISTORY_FILE  = "book_history.json"
OFFSET_FILE   = "telegram_offset.txt"
API_BASE      = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

VINTED_ITEM_URL = "https://www.vinted.co.uk/items/{item_id}"
VINTED_ITEM_API = "https://www.vinted.co.uk/api/v2/items/{item_id}"


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
    """Acknowledge the button tap so Telegram removes the loading spinner."""
    requests.post(f"{API_BASE}/answerCallbackQuery", json={
        "callback_query_id": callback_id,
        "text": text,
        "show_alert": False,
    }, timeout=10)


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
                "allowed_updates": ["callback_query"],
            }, timeout=40)

            if not resp.ok:
                time.sleep(5)
                continue

            updates = resp.json().get("result", [])

            for update in updates:
                offset = update["update_id"] + 1
                save_offset(offset)

                cq = update.get("callback_query")
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
                    answer_callback(callback_id, "✅ Logged as bought!")
                    edit_message_text(
                        chat_id, message_id,
                        f"✅ <b>BOUGHT</b> — {data.get('title', '')} @ £{data.get('price', '')}\n"
                        f"Logged to book_history.json — remember to update when sold."
                    )
                    print(f"  ✅ BOUGHT tapped: {data.get('title')}")

                elif action == "skip":
                    answer_callback(callback_id, "❌ Skipped")
                    edit_message_text(
                        chat_id, message_id,
                        f"❌ <b>SKIPPED</b> — {data.get('title', '')}"
                    )
                    print(f"  ❌ SKIP tapped: {data.get('title')}")

        except KeyboardInterrupt:
            print("\n⛔ Action handler stopped.")
            break
        except Exception as e:
            print(f"  [actions] Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    poll()