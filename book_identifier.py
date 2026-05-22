# book_identifier.py — extracts title, author, publisher and year from listing photos
#
# Only called when listing title is very short AND description is near-empty.
# Uses a cheap single-image call to read any visible text from the cover/spine.
# Results are injected back into the item dict before full scoring runs.

import base64
import json
import requests
from config import ANTHROPIC_API_KEY

ANTHROPIC_API = "https://api.anthropic.com/v1/messages"

EXTRACTION_PROMPT = """You are looking at a photo of a book listing from a second-hand marketplace.
The seller has provided very little information — your job is to read any visible text from the image.

Look carefully for:
- Title (on cover, spine or title page)
- Author name
- Publisher name (on spine, title page or base of spine)
- Publication year (on title page, copyright page, or spine)
- Any series name (e.g. "Golden Treasury Series", "Chandos Classics")
- Subject or genre clues from the cover design or visible chapter headings

Respond ONLY with a JSON object — no markdown, no preamble:
{
  "title": "extracted title or null",
  "author": "extracted author or null",
  "publisher": "extracted publisher or null",
  "year": 1874,
  "series": "extracted series or null",
  "genre_clues": ["any genre words visible on cover or spine"],
  "confidence": "high|medium|low"
}

If you cannot read any useful text, return:
{"title": null, "author": null, "publisher": null, "year": null, "series": null, "genre_clues": [], "confidence": "low"}
"""


def _download_image(url: str):
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        media_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
        b64 = base64.standard_b64encode(resp.content).decode("utf-8")
        return b64, media_type
    except Exception:
        return None


AGE_HINTS = {
    "old", "vintage", "antique", "victorian", "edwardian",
    "georgian", "1800", "1801", "1802", "1803", "1804", "1805",
    "1806", "1807", "1808", "1809", "1810", "1820", "1830",
    "1840", "1850", "1860", "1870", "1880", "1890",
    "leather", "gilt", "hardback", "illustrated",
}


def should_identify(item: dict) -> bool:
    """
    Returns True only when:
    - Title is 4 words or fewer AND description is under 20 characters
    - AND the title contains at least one age/value hint word
    This prevents wasting API calls on vague modern listings.
    """
    title       = (item.get("title") or "").strip()
    description = (item.get("description") or "").strip()
    title_words = len(title.split())
    if title_words > 4 or len(description) >= 20:
        return False
    title_lower = title.lower()
    return any(hint in title_lower for hint in AGE_HINTS)


def identify_book(item: dict) -> dict:
    """
    Send the first listing photo to Claude to extract visible text.
    Returns extracted metadata dict, or empty dict on failure.
    """
    photo_urls = item.get("photo_urls") or []
    if not photo_urls:
        photo_url = item.get("photo", "")
        photo_urls = [photo_url] if photo_url else []

    if not photo_urls:
        return {}

    image_data = _download_image(photo_urls[0])
    if not image_data:
        return {}

    b64_data, media_type = image_data

    payload = {
        "model":      "claude-sonnet-4-5",
        "max_tokens": 200,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type":       "base64",
                        "media_type": media_type,
                        "data":       b64_data,
                    }
                },
                {
                    "type": "text",
                    "text": EXTRACTION_PROMPT,
                }
            ]
        }]
    }

    headers = {
        "x-api-key":         ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type":      "application/json",
    }

    try:
        resp = requests.post(ANTHROPIC_API, json=payload, headers=headers, timeout=20)
        if not resp.ok:
            return {}
        data     = resp.json()
        raw_text = "".join(
            b["text"] for b in data.get("content", []) if b.get("type") == "text"
        ).strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1].lstrip("json").strip()
        result = json.loads(raw_text)
        # Track tokens used for cost reporting
        usage  = data.get("usage", {})
        result["_tokens_in"]  = usage.get("input_tokens", 0)
        result["_tokens_out"] = usage.get("output_tokens", 0)
        return result
    except Exception as e:
        print(f"  [identify] Error: {e}")
        return {}


def enrich_item(item: dict, identified: dict) -> dict:
    """
    Inject extracted metadata back into the item dict so the scorer
    can use it. Appends to title/description if useful info was found.
    """
    if not identified or identified.get("confidence") == "low":
        return item

    parts = []
    if identified.get("title"):
        parts.append(identified["title"])
    if identified.get("author"):
        parts.append(identified["author"])
    if identified.get("publisher"):
        parts.append(identified["publisher"])
    if identified.get("year"):
        parts.append(str(identified["year"]))
    if identified.get("series"):
        parts.append(identified["series"])
    if identified.get("genre_clues"):
        parts.extend(identified["genre_clues"])

    if parts:
        enriched = " ".join(parts)
        # Append to description so scorer picks it up via combined title+description
        existing_desc = item.get("description") or ""
        item["description"] = (existing_desc + " " + enriched).strip()
        print(f"  🔍 Identified: {enriched}")

    # If a year was extracted and no year_hint exists yet, set it
    if identified.get("year") and not item.get("year_hint"):
        try:
            item["year_hint"] = int(identified["year"])
        except (ValueError, TypeError):
            pass

    return item