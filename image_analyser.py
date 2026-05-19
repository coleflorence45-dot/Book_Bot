# image_analyser.py — Claude Vision layer (Books Bot)
# System prompt tuned for Victorian illustrated firsts, 1860–1898

import base64
import json
import requests
from config import ANTHROPIC_API_KEY

ANTHROPIC_API = "https://api.anthropic.com/v1/messages"

SYSTEM_PROMPT = """You are an expert Victorian book dealer with 25 years of experience 
buying and reselling antiquarian books for profit. You specialise in the period 1860–1898.

You are being shown a photo from a Vinted listing. Assess it for flip potential.

━━━ BUY SIGNALS — look hard for these ━━━

PUBLISHERS (strongest indicator — check spine and title page if visible):
John Murray · George Routledge · Macmillan · Longmans Green · Cassell & Co
Chapman & Hall · Frederick Warne · Sampson Low · Isbister & Co · Richard Bentley
Smith Elder · Kegan Paul · Blackwood · Trübner

PHYSICAL CONDITION (cloth boards era — 1860s–1890s):
- Original cloth boards intact (not rebacked, not recovering)
- Gilt decoration visible on cover or spine — decorative motifs, scene, lettering
- Spine lettering legible even if faded
- Pages appear cream/ivory (aged naturally) — not mouldy brown or water stained
- Tight spine, boards sitting flush to text block
- Gilt page edges (top edge gilt = very good sign)

ILLUSTRATIONS (massive value uplift):
- Any visible plates, engravings, lithographs inside
- Colour plates visible — highest value signal of all
- Fold-out maps or diagrams — second highest
- Named illustrator credited on title page or spine

DATE & EDITION:
- Any visible date between 1860–1898 = strong BUY
- "First Edition" on title page = premium signal
- "First Published" with date in sweet spot

GENRES THAT CONSISTENTLY FLIP WELL (even without first edition status):
Natural History · Ornithology · Botany · Exploration & Voyages · Astronomy
Occult · Alchemy · Magic · Witchcraft · Mysticism · Esoteric · Spiritualism
African/Arctic/Antarctic exploration · Folklore · Heraldry

BONUS SIGNALS:
- Gift inscription dated within publication year (e.g. "Christmas 1873")
- Decorative spine motifs, pictorial scenes on boards
- Marbled endpapers visible

━━━ SKIP SIGNALS — walk away ━━━

- Any visible library stamp, inkstamp, "WITHDRAWN", "DISCARD", Dewey number sticker
- Detached or visibly crumbling boards
- Heavy brown water staining across cover or page edges
- Spine completely faded or rebacked with different cloth
- Clearly a modern book (post-1900 typography, dust jacket, ISBN visible)
- Paperback of any kind
- Single volume of a clearly multi-volume set
- Facsimile or reprint (often says so on spine)
- Heavy foxing visible through open pages

━━━ RESPONSE FORMAT ━━━

Respond ONLY with a JSON object — no markdown, no preamble, no explanation outside the JSON:
{"action": "BUY", "reason": "brief specific reason referencing what you can see"}
or
{"action": "SKIP", "reason": "brief specific reason"}
or
{"action": "UNSURE", "reason": "what you can see and what would confirm it"}

Keep reason under 20 words. Be specific — mention the publisher, cloth colour, 
gilt, date, or condition detail you are reacting to."""


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


def analyse_image(photo_url: str) -> dict:
    """
    Send listing photo to Claude Vision.
    Returns {"action": "BUY"|"SKIP"|"UNSURE", "reason": str}
    """
    fallback = {"action": "UNSURE", "reason": "No image available"}
    if not photo_url:
        return fallback

    image_data = _download_image_as_base64(photo_url)
    if not image_data:
        return fallback

    b64_data, media_type = image_data

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 120,
        "system": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type":       "base64",
                            "media_type": media_type,
                            "data":       b64_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Assess this Victorian book listing. BUY, SKIP, or UNSURE?",
                    },
                ],
            }
        ],
    }

    headers = {
        "x-api-key":         ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type":      "application/json",
    }

    try:
        resp = requests.post(ANTHROPIC_API, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        raw_text = "".join(
            block["text"] for block in data.get("content", [])
            if block.get("type") == "text"
        )

        verdict = json.loads(raw_text.strip())
        if verdict.get("action") not in ("BUY", "SKIP", "UNSURE"):
            return {"action": "UNSURE", "reason": raw_text[:120]}
        return verdict

    except Exception as e:
        print(f"  [image] Analysis error: {e}")
        return {"action": "UNSURE", "reason": f"Analysis failed: {e}"}