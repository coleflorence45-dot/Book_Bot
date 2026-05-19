# scorer.py — Age & value signal scorer (Books Bot)
# Tuned for Victorian first editions 1860–1898

import re

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
# +1   short vague title (seller unawareness signal)
# +1   little or no description (seller unawareness signal)
# +1   publisher not named by seller (seller unawareness signal)
# +1   cheap + vague combo (classic undervalued find pattern)
# +1   price under £5
# -2   per BAD_TITLE_KEYWORD
# -3   post-1900 year detected
# -3   ex-library signals
# ──────────────────────────────────────────────────────────────────────────────

EX_LIBRARY_SIGNALS = [
    "ex library", "ex-library", "ex libris", "library stamp",
    "library plate", "shelf number", "shelf mark", "library sticker",
]

FIRST_EDITION_PHRASES = [
    "first edition", "1st edition", "first printing", "1st printing",
    "first published",
]

# At least one of these must appear for a listing to pass as a book or print.
# Prevents mirrors, jewellery, ceramics etc. scoring on "Victorian" / "antique" alone.
BOOK_CONTENT_INDICATORS = [
    # Explicit format words
    "book", "volume", "vol.", "edition", "hardback", "hardcover",
    "paperback", "softback", "published", "printed", "pages", "chapter",
    "illustrated", "illustrations", "plates", "engraving", "engravings",
    "lithograph", "atlas", "folio", "text", "manuscript", "pamphlet",
    "catalogue", "catalog", "journal", "almanac", "memoir", "memoirs",
    "essay", "essays", "treatise", "monograph", "dictionary", "encyclopaedia",
    "encyclopedia", "anthology", "annals", "gazette", "proceedings",
    "original plate", "antique print", "hand-coloured", "hand colored",
    "hand coloured", "chromolithograph", "woodcut", "mezzotint",
    # Subject/title words that appear almost exclusively in book titles
    # Covers "Birds of North America", "Mammals: A Guide...", "Origins" etc.
    "guide", "history", "origins", "origin", "natural", "nature", "wildlife",
    "species", "fauna", "flora", "birds", "bird", "mammals", "mammal",
    "fishes", "insects", "insect", "botany", "botanical", "geology",
    "astronomy", "celestial", "voyage", "voyages", "travels", "expedition",
    "exploration", "novel", "stories", "story", "tales", "tale", "narrative",
    "reader", "primer", "handbook", "manual", "companion", "introduction",
    "observations", "observations", "lectures", "letters", "works of",
    "collected", "selected", "complete works", "essays of",
]


# Words that — when found in the title — indicate a standalone print, not a book.
# Using word-boundary sets avoids Unicode dash / separator issues entirely.
PRINT_TITLE_NOUNS = {"print", "prints", "engraving", "engravings"}

# A listing matching a print noun is still OK if it clearly IS a book.
STRONG_BOOK_WORDS = {
    "book", "volume", "hardback", "hardcover",
    "paperback", "softback", "edition", "leatherbound",
}


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

    # ── Seller unawareness signals ────────────────────────────────────────────
    # Sparse listings are a strong indicator the seller doesn't know the value.
    # These are the listings that consistently produce the best flips.
    title       = (item.get("title") or "")
    description = (item.get("description") or "").strip()
    title_words = len(title.split())

    # Very short title — seller hasn't done research
    if title_words <= 5:
        score += 1
        signals.append("🔍 Vague short title")

    # No meaningful description — listed quickly without knowledge
    if len(description) < 30:
        score += 1
        signals.append("🔍 Little or no description")

    # No publisher named anywhere in title or description
    publisher_mentioned = any(pub.lower() in combined for pub in PUBLISHER_SIGNALS)
    if not publisher_mentioned:
        score += 1
        signals.append("🔍 Publisher not identified by seller")

    # Cheap + vague combo — the classic undervalued find pattern
    if price <= 8.0 and title_words <= 6 and len(description) < 50:
        score += 1
        signals.append("💎 Cheap + vague = likely undervalued")

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

    # Individual pages or cuttings sold from books — not a complete book
    # e.g. "Antique Lithograph from 1874 - cutting from book"
    # e.g. "Vintage Palm and Date Illustrated Book Plate"
    CUTTING_PHRASES = [
        "cutting from book", "cut from book",
        "page from book", "pages from book",
        "taken from book", "removed from book",
        "from a book", "from an old book",
        "book plate", "book-plate", "bookplate",
    ]
    title_lower = (item.get("title") or "").lower()
    if any(phrase in title_lower for phrase in CUTTING_PHRASES):
        return True, "Individual page/cutting from a book (not a complete book)"

    # Single print/illustration — not a book.
    # Extract individual words from the title and check for print nouns.
    # Word-boundary approach avoids Unicode dash/separator issues entirely.
    title_words = set(re.findall(r'\b\w+\b', (item.get("title") or "").lower()))
    if (title_words & PRINT_TITLE_NOUNS) and not (title_words & STRONG_BOOK_WORDS):
        return True, "Single print/illustration (not a book)"

    # Not a book or print at all — mirrors, jewellery, ceramics etc.
    # We pass if ANY book/print content word is present OR if a genre signal is
    # present (subject-matter titles like "Natural History of Britain" contain
    # neither "book" nor "hardback" but are obviously books).
    has_book_word  = any(ind in combined for ind in BOOK_CONTENT_INDICATORS)
    has_genre_word = any(g in combined for g in TARGET_GENRE_SIGNALS)
    if not has_book_word and not has_genre_word:
        return True, "No book/print content indicators found"

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