# telegram_bot.py — Telegram alert sender (Books Bot)

import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def _verdict_emoji(action: str) -> str:
    return {"BUY": "🟢", "SKIP": "🔴", "UNSURE": "🟡"}.get(action, "⚪")


def send_alert(item: dict):
    """
    Send a formatted Telegram message for a new book listing.
    Includes score, age signals, and the Claude Vision verdict.
    """
    signals_text = "\n".join(item.get("signals", [])) if item.get("signals") else "—"

    verdict       = item.get("image_verdict") or {}
    verdict_action = verdict.get("action", "UNSURE")
    verdict_reason = verdict.get("reason", "")
    verdict_line   = f"{_verdict_emoji(verdict_action)} *Image: {verdict_action}* — {verdict_reason}"

    year_line = f"📅 Year hint: {item['year_hint']}" if item.get("year_hint") else ""

    # Build message
    lines = [
        f"📚 *{item['title']}*",
        f"💰 £{item['price']:.2f}  |  Score: {item['score']}",
        f"⭐ Condition: {item['condition']}",
        f"👤 Seller: {item['seller']} ({item['seller_rep']} feedback)",
    ]
    if year_line:
        lines.append(year_line)
    lines += [
        "",
        "*Signals detected:*",
        signals_text,
        "",
        verdict_line,
        "",
        f"🔗 {item['url']}",
    ]

    message = "\n".join(lines)

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       message,
        "parse_mode": "Markdown",
    }

    try:
        resp = requests.post(url, data=payload, timeout=10)
        if not resp.ok:
            print(f"  [telegram] Send failed: {resp.status_code} {resp.text[:100]}")
    except Exception as e:
        print(f"  [telegram] Error: {e}")


def send_image(photo_url: str):
    """Optionally send the book photo alongside the alert."""
    if not photo_url:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo":   photo_url,
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"  [telegram] Photo send error: {e}")