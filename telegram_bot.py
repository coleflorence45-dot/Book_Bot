# telegram_bot.py — Telegram alert sender (Books Bot)

import html
import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def _e(text) -> str:
    """Escape special HTML characters in dynamic content."""
    return html.escape(str(text or ""))


def _verdict_emoji(action: str) -> str:
    return {"BUY": "🟢", "SKIP": "🔴", "UNSURE": "🟡"}.get(action, "⚪")


def send_alert(item: dict):
    """Send a formatted Telegram message for a new book listing."""
    signals_text = "\n".join(item.get("signals", [])) if item.get("signals") else "—"

    verdict        = item.get("image_verdict") or {}
    verdict_action = verdict.get("action", "UNSURE")
    verdict_reason = _e(verdict.get("reason", ""))
    verdict_line   = f"{_verdict_emoji(verdict_action)} <b>Image: {verdict_action}</b> — {verdict_reason}"

    year_line = f"📅 Year hint: {_e(item['year_hint'])}" if item.get("year_hint") else ""

    lines = [
        f"📚 <b>{_e(item['title'])}</b>",
        f"💰 £{float(item['price']):.2f}  |  Score: {item['score']}",
        f"⭐ Condition: {_e(item['condition'])}",
        f"👤 Seller: {_e(item['seller'])} ({_e(item['seller_rep'])} feedback)",
    ]
    if year_line:
        lines.append(year_line)
    lines += [
        "",
        "<b>Signals:</b>",
        _e(signals_text),
        "",
        verdict_line,
        "",
        f"🔗 {_e(item['url'])}",
    ]

    message = "\n".join(lines)
    url     = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       message,
        "parse_mode": "HTML",
    }

    try:
        resp = requests.post(url, data=payload, timeout=10)
        if not resp.ok:
            print(f"  [telegram] Send failed: {resp.status_code} {resp.text[:200]}")
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"  [telegram] Error: {e}")


def send_image(photo_url: str):
    """Send the book photo alongside the alert."""
    if not photo_url:
        return
    url     = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "photo": photo_url}
    try:
        requests.post(url, data=payload, timeout=10)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"  [telegram] Photo send error: {e}")