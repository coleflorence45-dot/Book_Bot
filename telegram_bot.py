# telegram_bot.py — Telegram alert sender (Books Bot)

import html
import json
import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from pricing import format_price_line


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
    fav_count   = item.get("favourites", 0) or 0
    listing_age = item.get("listing_age")
    if fav_count >= 5 and listing_age is not None and listing_age <= 40:
        fav_line = f"🔥 {fav_count} favourites in {listing_age} minutes — act fast"
    elif fav_count >= 5:
        fav_line = f"❤️ {fav_count} favourites"
    else:
        fav_line = ""

    # Market value lines — AbeBooks (asking) and eBay (sold)
    abebooks     = item.get("market_abebooks") or {}
    ebay         = item.get("market_ebay")     or {}
    market_lines = []

    if ebay.get("found"):
        if ebay.get("confirmed_flip"):
            market_lines.append(
                f"🔥 <b>eBay SOLD: £{ebay['median_sold']:.2f} median</b> "
                f"(range £{ebay['lowest_sold']:.2f}–£{ebay['highest_sold']:.2f} · {ebay['multiple']}x your price)"
            )
        else:
            market_lines.append(
                f"📦 eBay sold: £{ebay['median_sold']:.2f} median "
                f"(£{ebay['lowest_sold']:.2f}–£{ebay['highest_sold']:.2f})"
            )

    if abebooks.get("found"):
        if abebooks.get("confirmed_flip"):
            market_lines.append(
                f"🔥 <b>AbeBooks asking: from £{abebooks['lowest_price']:.2f}</b> "
                f"({abebooks['multiple']}x your price)"
            )
        else:
            market_lines.append(
                f"📖 AbeBooks asking: from £{abebooks['lowest_price']:.2f} "
                f"(median £{abebooks['median_price']:.2f})"
            )

    # Recommended sell price
    pricing      = item.get("pricing") or {}
    pricing_line = format_price_line(pricing, float(item.get("price", 0))) if pricing else ""

    lines = [
        f"📚 <b>{_e(item['title'])}</b>",
        f"💰 £{float(item['price']):.2f}  |  Score: {item['score']}",
        f"⭐ Condition: {_e(item['condition'])}",
        f"👤 Seller: {_e(item['seller'])} ({_e(item['seller_rep'])} feedback)",
    ]
    if year_line:
        lines.append(year_line)
    if fav_line:
        lines.append(fav_line)
    if market_lines:
        lines += market_lines
    if pricing_line:
        lines += ["", pricing_line]
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

    # ── Callback data — strict 64-byte limit ──────────────────────────────────
    # Keep only what telegram_actions.py needs to log a purchase.
    # The Vinted URL is reconstructed from item_id on the receiving end.
    # Format: action|item_id|price|short_title
    item_id    = str(item.get("id", ""))
    price_str  = str(float(item.get("price", 0)))
    # Trim title to fit within 64 bytes total for the bought callback
    # "bought|" (7) + item_id (≤12) + "|" + price (≤6) + "|" = ~26 chars overhead
    max_title  = 64 - 7 - len(item_id) - 1 - len(price_str) - 1
    short_title = (item.get("title") or "")[:max(0, max_title)]

    inline_keyboard = {"inline_keyboard": [[
        {"text": "✅ Bought",
         "callback_data": f"bought|{item_id}|{price_str}|{short_title}"},
        {"text": "❌ Skip",
         "callback_data": f"skip|{item_id}"},
    ]]}

    payload = {
        "chat_id":      TELEGRAM_CHAT_ID,
        "text":         message,
        "parse_mode":   "HTML",
        "reply_markup": json.dumps(inline_keyboard),
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