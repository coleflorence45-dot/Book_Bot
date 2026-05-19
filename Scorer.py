# scorer.py — Age & value signal scorer (Books Bot)
# Tuned for Victorian first editions 1860–1898

from config import (
    AGE_SIGNALS,
    ILLUSTRATION_BONUS_SIGNALS,
    PUBLISHER_SIGNALS,
    TARGET_GENRE_SIGNALS,
    BAD_TITLE_KEYWORDS,
    YEAR_SWEET_SPOT_START,
    YEAR_SWEET_SPOT_END,
    HARD_BLOCK_AFTER_YEAR,
)

# ── Scoring breakdown ──────────────────────────────────────────────────────────
# +3   first / 1st edition detected
# +2   per publisher in PUBLISHER_SIGNALS
# +2   per entry in ILLUSTRATION_BONUS_SIGNALS (colour plates, fold-out maps)
# +2   year within sweet spot 1860–1898
# +1   year present and pre-1900 (but outside sweet spot)
# +1   per AGE_SIGNAL keyword
# +1   per TARGET_GENRE_SIGNAL
# +1   price under £5 (seller likely unaware of value)
# -2   per BAD_TITLE_KEYWORD
# -3   post-1900 year detected (nearly always a hard block too)
# -3   ex-library signals (double-penalised — kills most deals)
# ──────────────────────────────────────────────────────────────────────────────

EX_LIBRARY_SIGNALS = [
    "ex library", "ex-library", "ex libris", "library stamp",
    "library plate", "shelf number", "shelf mark", "library sticker",
]

FIRST_EDITION_PHRASES = [
    "first edition", "1st edition", "first printing", "1st printing",
    "first published",
]


def _combined(item: dict) -> str:
    return ((item.get("title") or "") + " " + (item.get("description") or "")).lower()


def score_item(item: dict) -> dict:
    """
    Populate item['score'] and item['signals'].
    Returns the item (mutated in place).
    """
    combined = _combined(item)
    signals  = []
    score    = 0

    # ── First edition — premium signal ────────────────────────────────────────
    for phrase in FIRST_EDITION_PHRASES:
        if phrase in combined:
            score += 3
            signals.append("🥇 First edition")
            break   # only award once

    # ── Publisher match ────────────────────────────────────────────────────────
    for pub in PUBLISHER_SIGNALS:
        if pub.lower() in combined:
            score += 2
            signals.append(f"🏛️ Publisher: {pub.title()}")
            break   # award once per listing (multiple matches = same publisher)

    # ── Illustration bonus signals ─────────────────────────────────────────────
    for sig in ILLUSTRATION_BONUS_SIGNALS:
        if sig.lower() in combined:
            score += 2
            signals.append(f"🎨 {sig.title()}")

    # ── Target genre ──────────────────────────────────────────────────────────
    for genre in TARGET_GENRE_SIGNALS:
        if genre.lower() in combined:
            score += 1
            signals.append(f"📂 {genre.title()}")
            break   # one genre match is enough — avoid score inflation

    # ── Age signals ───────────────────────────────────────────────────────────
    for sig in AGE_SIGNALS:
        if sig.lower() in combined:
            score += 1
            signals.append(f"📖 {sig.title()}")

    # ── Year hint ─────────────────────────────────────────────────────────────
    year = item.get("year_hint")
    if year:
        if year > HARD_BLOCK_AFTER_YEAR:
            score -= 3
            signals.append(f"🚫 Post-1900 year ({year})")
        elif YEAR_SWEET_SPOT_START <= year <= YEAR_SWEET_SPOT_END:
            score += 2
            signals.append(f"📅 Sweet spot year: {year}")
        elif year < YEAR_SWEET_SPOT_START:
            score += 1
            signals.append(f"📅 Pre-1860: {year} (check carefully)")
        else:
            # 1899–1900 range — marginal, no bonus, no penalty
            signals.append(f"📅 Year: {year} (borderline era)")

    # ── Price bonus ───────────────────────────────────────────────────────────
    price = item.get("price", 999)
    if price <= 5.0:
        score += 1
        signals.append("💸 Low price — seller likely unaware of value")

    # ── Bad keyword penalties ─────────────────────────────────────────────────
    for bad in BAD_TITLE_KEYWORDS:
        if bad.lower() in combined:
            score -= 2
            signals.append(f"⚠️ {bad}")

    # ── Ex-library: extra penalty on top of bad keywords ──────────────────────
    for ex in EX_LIBRARY_SIGNALS:
        if ex in combined:
            score -= 3
            signals.append("🚫 Ex-library (walk away)")
            break

    item["score"]   = score
    item["signals"] = signals
    return item


def hard_block(item: dict) -> tuple[bool, str]:
    """
    Returns (True, reason) if the listing should be skipped unconditionally,
    regardless of score. These are your absolute walk-away rules.
    """
    combined = _combined(item)

    # Post-1900 year in title
    year = item.get("year_hint")
    if year and year > HARD_BLOCK_AFTER_YEAR:
        return True, f"Post-1900 year detected ({year})"

    # Ex-library
    for ex in EX_LIBRARY_SIGNALS:
        if ex in combined:
            return True, "Ex-library copy"

    # Missing plates — illustrated books are only valuable when complete
    if "missing plates" in combined or "plates missing" in combined or "plates removed" in combined:
        return True, "Missing plates"

    # Detached boards
    if "detached boards" in combined or "boards detached" in combined:
        return True, "Detached boards"

    # Facsimile / reprint
    for term in ("facsimile", "fascimile", "modern reprint", "reproduction copy"):
        if term in combined:
            return True, f"Reprint/facsimile ({term})"

    return False, ""


def passes_condition_filter(item: dict, good_conditions: list) -> bool:
    return item.get("condition", "").lower() in [c.lower() for c in good_conditions]