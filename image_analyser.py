# image_analyser.py — Claude Vision layer (Books Bot)
# System prompt tuned for Victorian illustrated firsts, 1860–1898

import base64
import json
import requests
from config import ANTHROPIC_API_KEY

ANTHROPIC_API = "https://api.anthropic.com/v1/messages"

SYSTEM_PROMPT = """You are a strict, experienced Victorian antiquarian book dealer. You only buy books 
you are confident can be flipped for significant profit. You are being shown a Vinted listing photo.

Your target: substantive Victorian books (1860–1898) in good condition with clear resale value.
Be conservative — say UNSURE rather than BUY if you have any doubt. Only say BUY when genuinely confident.

━━━ HARD SKIP — reject immediately if you see any of these ━━━

CONDITION FAILURES:
- Heavily worn, rubbed, or faded cloth with no gilt remaining
- Boards detached, cracked, or heavily bumped at corners
- Spine faded to a completely different colour from boards
- Any visible staining, water damage, or mould
- Pages visibly yellowed-brown (beyond natural cream aging) or foxed throughout

SIZE / SUBSTANCE FAILURES (this is critical):
- Thin spine — if the book looks under ~2cm thick it is likely a pamphlet, 
  school reader, primer, or workbook — these have very limited resale value
- Small octavo or duodecimo format school textbooks — cheap institutional bindings
  with no decorative features are not worth buying
- Any book described or appearing as a "reader", "primer", or "exercise book"

PROVENANCE FAILURES:
- Any visible library stamp, sticker, Dewey number, or "WITHDRAWN" marking
- Ex-library binding (reinforced corners, plastic spine protectors)

MODERN / WRONG ERA:
- Dust jacket present = almost certainly post-1920s, skip
- Clean white/cream paper visible = modern printing, skip
- ISBN or barcode visible = skip
- Post-1898 publication date visible anywhere

━━━ BUY — say BUY only if ALL of these are true ━━━

1. SUBSTANTIAL SIZE: Spine looks at least 2–3cm thick — a proper volume, not a pamphlet
2. CLOTH CONDITION: Original cloth boards present and in at least good condition — 
   some wear acceptable but gilt or decorative design must still be visible
3. ERA: Looks genuinely Victorian — aged paper edges visible, period typography, 
   no dust jacket, cloth or leather binding only
4. APPEAL: At least one of: gilt spine lettering visible, decorative cover design or scene, 
   colour plates visible inside, named publisher from a known quality imprint

━━━ PUBLISHERS to look for on spine or title page ━━━
John Murray · Macmillan · Chapman & Hall · Cassell · Longmans · Frederick Warne
Sampson Low · George Routledge · Richard Bentley · Smith Elder · Blackwood

━━━ GENRES that command highest prices ━━━
Natural History · Ornithology · Botany · Exploration & Voyages · Astronomy
Occult · Alchemy · Mysticism · Spiritualism · African/Arctic expedition accounts

━━━ RESPONSE FORMAT ━━━
Respond ONLY with JSON — no markdown, no preamble:
{"action": "BUY", "reason": "specific visual reason — mention what you can see"}
{"action": "SKIP", "reason": "specific reason for rejection"}
{"action": "UNSURE", "reason": "what is unclear and what would confirm it"}

BUY = confident this is a genuine Victorian volume worth flipping
SKIP = clear reason to reject
UNSURE = promising but cannot confirm from photo alone

Keep reason under 20 words. Be specific."""


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
        "model": "claude-sonnet-4-5",
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
        if not resp.ok:
            print(f"  [image] API error {resp.status_code}: {resp.text[:120]}")
            return {"action": "UNSURE", "reason": f"API error {resp.status_code}"}
        data = resp.json()

        raw_text = "".join(
            block["text"] for block in data.get("content", [])
            if block.get("type") == "text"
        ).strip()

        if not raw_text:
            return {"action": "UNSURE", "reason": "Empty response from model"}

        # Strip markdown fences if the model wrapped the JSON anyway
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[-2] if "```" in raw_text else raw_text
            raw_text = raw_text.lstrip("json").strip()

        verdict = json.loads(raw_text)
        if verdict.get("action") not in ("BUY", "SKIP", "UNSURE"):
            return {"action": "UNSURE", "reason": raw_text[:120]}
        return verdict

    except KeyboardInterrupt:
        raise  # let main.py handle clean exit
    except Exception as e:
        print(f"  [image] Analysis error: {e}")
        return {"action": "UNSURE", "reason": f"Analysis failed: {e}"}