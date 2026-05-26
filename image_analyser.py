# image_analyser.py — Claude Vision layer (Books Bot)
#
# Multi-photo strategy: all listing photos are sent in ONE API call.
# Claude identifies what each photo shows (title page, spine, cover, etc.)
# and prioritises accordingly — title page > spine > cover > back.
# Single-photo listings use the same call, just with one image.
#
# This is both cheaper (1 call vs up to 5) and more accurate (the model
# can cross-reference a title page year against the cover condition).

import base64
import json
import os
import re
import requests
from config import ANTHROPIC_API_KEY

ANTHROPIC_API        = "https://api.anthropic.com/v1/messages"
HISTORY_FILE         = "book_history.json"
MIN_PROFIT_THRESHOLD = 10.0
MAX_REFERENCE_PHOTOS = 3
MAX_LISTING_PHOTOS   = 5

MODEL = "claude-sonnet-4-6"

# ── System prompt ──────────────────────────────────────────────────────────────
# When multiple photos are present, the model is instructed to find and
# prioritise the most informative ones before making a verdict.
# Title page > spine > cover > interior pages > back cover.

SYSTEM_PROMPT = """You are a Victorian antiquarian book dealer assessing Vinted listing photos.
Your goal: identify books published 1800–1910 that can be profitably resold.

━━━ WHEN MULTIPLE PHOTOS ARE SHOWN ━━━

First, mentally identify what each photo shows:
  cover | spine | title_page | interior | back_cover | detail

Then extract information in this priority order — these tell you the most:
  1. Title page  → publication year, publisher, author, series name
  2. Spine       → publisher, title, condition, gilt or decoration
  3. Cover       → aesthetic appeal, cloth colour, gilt, condition, era
  4. Interior    → plate quality, paper age, completeness
  5. Back / detail → condition specifics

Use ALL available evidence when making your verdict.
A title page showing "Chapman & Hall, 1874" plus a cover with intact gilt boards = BUY.
A cover alone with no year or publisher = UNSURE (unless unmistakably modern → SKIP).

━━━ HARD SKIP — reject immediately ━━━

Modern book signals (any one = SKIP):
• Dust jacket present
• ISBN or barcode visible
• Clean bright-white paper — modern printing
• Post-1910 publication date clearly visible on title page or spine

Damage signals (any one = SKIP):
• Ex-library — stamps, stickers, Dewey shelf numbers, "WITHDRAWN", reinforced spine
• Boards completely detached or hanging off
• Visible mould, heavy water staining
• Spine missing entirely

Wrong item signals (any one = SKIP):
• Thin booklet / pamphlet / school primer — spine under ~1cm
• Single print or page torn from a book — not a complete volume
• Theology / divinity / sermons — slow category regardless of age or binding
  (commentaries, epistles, doctrinal works, homilies, patristics)

━━━ BUY — weighted signals, not a strict checklist ━━━

From title page or spine (any ONE is strong evidence):
• Victorian/Edwardian year (1800–1910) visible
• Quality publisher visible: John Murray · Macmillan · Chapman & Hall · Cassell
  Longmans · Frederick Warne · Sampson Low · Routledge · Smith Elder · Blackwood · Bentley
• Named series: Golden Treasury · Chandos Classics · Morley's Universal Library · etc.

From cover (any ONE is a strong positive):
• Gilt lettering or decoration visible — even partial gilt counts
• Pictorial or embossed scene on boards
• Rich coloured cloth (deep red, forest green, navy, purple, crimson) in good condition
• Art Nouveau, Arts & Crafts, or ornate decorative motifs on cover

Subject signals (genre adds value):
• Natural history, ornithology, botany, astronomy, occult, exploration/voyages visible

Condition threshold:
  Acceptable: rubbed corners, faded cloth, light foxing, minor bumping.
  These are NOT skip reasons — a worn decorated Victorian book beats a pristine plain one.

━━━ THE UNDERVALUED SELLER HEURISTIC ━━━

If the book looks genuinely Victorian (aged cloth, no dust jacket, period typography)
AND shows any decorative or aesthetic feature (even faint gilt)
→ lean BUY. Uninformed sellers who don't know what they have are the whole point.

━━━ RESPONSE FORMAT ━━━

Respond ONLY with a JSON object. No markdown, no preamble, no text outside the JSON.

If you can make a verdict:
{"action": "BUY", "reason": "what you found — title page year/publisher, cover features"}
{"action": "SKIP", "reason": "specific disqualifying evidence you found"}

If genuinely unresolvable:
{"action": "UNSURE", "reason": "what is missing and which photo type would resolve it"}

Reason: be specific. Mention what you actually read or saw. Under 25 words."""


def _load_reference_examples() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        books = data.get("books", [])
        good  = [
            b for b in books
            if not b.get("_example")
            and b.get("photos")
            and (
                float(b.get("profit", 0) or 0) >= MIN_PROFIT_THRESHOLD
                or (b.get("bought_price") and b.get("sold_price") is None)
            )
        ]
        good.sort(
            key=lambda b: (b.get("sold_price") is not None, float(b.get("profit", 0) or 0)),
            reverse=True
        )
        return good
    except Exception as e:
        print(f"  [image] Could not load history: {e}")
        return []


def _build_reference_content(examples: list) -> list:
    if not examples:
        return []

    content = []
    lines   = ["━━━ REFERENCE EXAMPLES — books this buyer has purchased ━━━\n"]
    photo_count = 0

    for i, book in enumerate(examples[:MAX_REFERENCE_PHOTOS * 2]):
        title  = book.get("title", "Unknown")
        profit = book.get("profit")
        notes  = book.get("notes", "")
        bought = book.get("bought_price", "?")
        sold   = book.get("sold_price")
        photos = book.get("photos", [])

        if sold and profit:
            line = f"Example {i+1}: '{title}' — bought £{bought}, sold £{sold} (+£{profit})"
        else:
            line = f"Example {i+1}: '{title}' — bought £{bought} (held in stock)"
        if notes:
            line += f" — {notes}"
        lines.append(line)

        if photos and photo_count < MAX_REFERENCE_PHOTOS:
            photo_b64 = photos[0]
            if "," in photo_b64:
                photo_b64 = photo_b64.split(",", 1)[1]
            label = f"+£{profit}" if profit else "recent buy"
            content.append({"type": "text",
                             "text": f"Reference {photo_count+1}: {title} ({label}):"})
            content.append({"type": "image", "source": {
                "type": "base64", "media_type": "image/jpeg", "data": photo_b64
            }})
            photo_count += 1

    lines.append("\nUse these as visual references — calibrate your expectations to books like these.")
    content.insert(0, {"type": "text", "text": "\n".join(lines)})
    return content


def _download_image_as_base64(url: str):
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        media_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
        b64 = base64.standard_b64encode(resp.content).decode("utf-8")
        return b64, media_type
    except Exception as e:
        print(f"  [image] Download failed: {e}")
        return None


def _extract_json_verdict(raw_text: str) -> dict:
    """
    Pull a BUY/SKIP/UNSURE JSON object from the model response.
    Handles cases where the model includes identification notes before the JSON.
    """
    # Try direct parse first
    stripped = raw_text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("```")[1].lstrip("json").strip()
    try:
        return json.loads(stripped)
    except Exception:
        pass

    # Find JSON object anywhere in the response
    match = re.search(r'\{[^{}]+\}', raw_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    return {"action": "UNSURE", "reason": raw_text[:120]}


def _analyse_photos(downloaded: list, reference_content: list) -> dict:
    """
    Send all listing photos in a single API call.
    Claude identifies what each photo shows and prioritises accordingly.
    """
    total = len(downloaded)

    user_content = list(reference_content)

    if total == 1:
        intro = (
            "━━━ NEW LISTING — 1 photo ━━━\n"
            "Assess this photo and give a verdict."
        )
    else:
        intro = (
            f"━━━ NEW LISTING — {total} photos ━━━\n"
            f"These are all photos from a single Vinted listing.\n"
            f"Identify what each photo shows (title page, spine, cover, interior, back, detail).\n"
            f"Extract information in priority order: title page first, then spine, then cover.\n"
            f"Use ALL available evidence to give a single final verdict."
        )

    user_content.append({"type": "text", "text": intro})

    for i, (b64_data, media_type) in enumerate(downloaded):
        user_content.append({
            "type": "text",
            "text": f"Photo {i + 1}:"
        })
        user_content.append({
            "type": "image",
            "source": {
                "type":       "base64",
                "media_type": media_type,
                "data":       b64_data,
            }
        })

    user_content.append({
        "type": "text",
        "text": "Final verdict — JSON only: BUY, SKIP, or UNSURE."
    })

    payload = {
        "model":      MODEL,
        "max_tokens": 200,
        "system":     SYSTEM_PROMPT,
        "messages":   [{"role": "user", "content": user_content}],
    }

    headers = {
        "x-api-key":         ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type":      "application/json",
    }

    resp = requests.post(ANTHROPIC_API, json=payload, headers=headers, timeout=60)
    if not resp.ok:
        return {"action": "UNSURE", "reason": f"API error {resp.status_code}",
                "input_tokens": 0, "output_tokens": 0}

    data     = resp.json()
    usage    = data.get("usage", {})
    raw_text = "".join(
        b["text"] for b in data.get("content", []) if b.get("type") == "text"
    ).strip()

    verdict = _extract_json_verdict(raw_text)

    if verdict.get("action") not in ("BUY", "SKIP", "UNSURE"):
        verdict = {"action": "UNSURE", "reason": raw_text[:120]}

    verdict["input_tokens"]  = usage.get("input_tokens", 0)
    verdict["output_tokens"] = usage.get("output_tokens", 0)
    return verdict


def analyse_image(photo_url: str, photo_urls: list = None) -> dict:
    """
    Download all listing photos and send them to Claude in a single API call.
    Claude identifies the most informative photos (title page, spine) and
    uses them to reach the most accurate verdict possible.

    Returns final verdict dict with token usage.
    """
    fallback = {"action": "UNSURE", "reason": "No image available",
                "input_tokens": 0, "output_tokens": 0}

    # Build deduplicated URL list
    urls_to_use = []
    if photo_urls:
        seen_urls = set()
        for u in photo_urls:
            if u and u not in seen_urls:
                urls_to_use.append(u)
                seen_urls.add(u)
        urls_to_use = urls_to_use[:MAX_LISTING_PHOTOS]
    elif photo_url:
        urls_to_use = [photo_url]

    if not urls_to_use:
        return fallback

    # Download all photos
    downloaded = []
    for url in urls_to_use:
        result = _download_image_as_base64(url)
        if result:
            downloaded.append(result)

    if not downloaded:
        return fallback

    total = len(downloaded)
    if total > 1:
        print(f"  [image] Sending all {total} photos in one call (title page priority)")
    else:
        print(f"  [image] Analysing 1 photo")

    examples          = _load_reference_examples()
    reference_content = _build_reference_content(examples)
    if examples:
        print(f"  [image] Using {len(examples)} history reference(s)")

    try:
        verdict = _analyse_photos(downloaded, reference_content)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"  [image] Analysis error: {e}")
        verdict = {"action": "UNSURE", "reason": f"Analysis error: {str(e)[:60]}",
                   "input_tokens": 0, "output_tokens": 0}

    action = verdict.get("action", "UNSURE")
    reason = verdict.get("reason", "")
    print(f"  [image] {action}: {reason}")

    return verdict