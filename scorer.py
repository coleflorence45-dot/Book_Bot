# scorer.py — Age & value signal scorer (Books Bot)
# Tuned for Victorian first editions 1860–1898

import re

from config import (
    AGE_SIGNALS,
    ILLUSTRATION_BONUS_SIGNALS,
    AESTHETIC_BONUS_SIGNALS,
    PUBLISHER_SIGNALS,
    PUBLISHER_TIER_1,
    AUTHOR_WHITELIST,
    PHYSICAL_DESCRIPTOR_SIGNALS,
    TARGET_GENRE_SIGNALS,
    PRIORITY_GENRE_ASTRONOMY,
    PRIORITY_GENRE_NATURAL_HISTORY,
    PRIORITY_GENRE_OCCULT,
    BAD_TITLE_KEYWORDS,
    YEAR_SWEET_SPOT_START,
    YEAR_SWEET_SPOT_END,
    HARD_BLOCK_AFTER_YEAR,
    HARD_BLOCK_AFTER_YEAR_PRIORITY,
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
    "observations", "lectures", "letters", "works of",
    "collected", "selected", "complete works", "essays of",
    # Trade, reference and technical titles often listed without "book"
    "receipts", "workshop", "mechanics", "manufacture", "manufactures",
    "treatise on", "principles of", "elements of", "theory of",
    "history of", "lives of", "life of", "memoirs of", "narrative of",
    "account of", "description of", "guide to", "introduction to",
    "recollections", "reminiscences", "autobiography", "biography",
    "sermons", "lectures", "poems", "poetry", "poetical", "prose",
    "dramas", "plays", "novels", "tales", "legends", "mythology",
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

    # ── Condition bonus/penalty ───────────────────────────────────────────────
    condition = (item.get("condition") or "").lower()
    if "new with tags" in condition or "new without tags" in condition:
        score += 2
        signals.append("✨ Condition: New (+2)")
    elif "very good" in condition:
        score += 2
        signals.append("⭐ Condition: Very Good (+2)")
    elif "good" in condition:
        score += 1
        signals.append("👍 Condition: Good (+1)")
    elif "satisfactory" in condition:
        score -= 1
        signals.append("⚠️ Condition: Satisfactory (-1)")

    # ── First edition — only score if Victorian/period context confirmed ────────
    # Without a period year or known publisher, "1st edition" could be anything.
    # HP Deathly Hallows 1st ed, Twilight 1st ed, etc. should NOT score here.
    has_period_context = (
        (item.get("year_hint") and int(item.get("year_hint")) <= 1910) or
        any(pub.lower() in combined for pub in PUBLISHER_SIGNALS)
    )
    for phrase in FIRST_EDITION_PHRASES:
        if phrase in combined and has_period_context:
            score += 2
            signals.append("🥇 First edition (+2)")
            break

    # ── Publisher match — tiered weighting ────────────────────────────────────
    # Tier 1 (John Murray, Macmillan, Chapman & Hall, Smith Elder, Blackwood,
    #         Kegan Paul) score +3 — their imprint alone signals collector value.
    # All other PUBLISHER_SIGNALS score +2.
    # Points awarded once per listing regardless of how many publishers appear.
    pub_found = None
    for pub in PUBLISHER_TIER_1:
        if pub.lower() in combined:
            pub_found = pub
            break
    if pub_found:
        score += 3
        signals.append(f"🏛️ Tier-1 publisher: {pub_found.title()} (+3)")
    else:
        for pub in PUBLISHER_SIGNALS:
            if pub.lower() in combined:
                score += 2
                signals.append(f"🏛️ Publisher: {pub.title()}")
                break

    # ── Author whitelist ───────────────────────────────────────────────────────
    # Known Victorian/Edwardian authors — mild positive signal only.
    # +1 because popular literary authors (Dickens, Kipling) are not the primary
    # target; genre signals (natural history, occult, astronomy) carry far more
    # weight. Author presence just breaks ties and confirms era.
    for author in AUTHOR_WHITELIST:
        if author.lower() in combined:
            score += 1
            signals.append(f"✍️ Known author: {author.title()} (+1)")
            break

    # ── Physical descriptor signals ────────────────────────────────────────────
    # Binding terms used by sellers who've actually examined the book.
    # +2 each, capped at 2 matches — stacking beyond 2 is likely the same feature.
    phys_found = []
    for sig in PHYSICAL_DESCRIPTOR_SIGNALS:
        if sig.lower() in combined:
            phys_found.append(sig)
        if len(phys_found) == 2:
            break
    for sig in phys_found:
        score += 2
        signals.append(f"📐 {sig.title()} (+2)")

    # ── Illustration bonus signals ─────────────────────────────────────────────
    for sig in ILLUSTRATION_BONUS_SIGNALS:
        if sig.lower() in combined:
            score += 2
            signals.append(f"🎨 {sig.title()}")

    # ── Aesthetic bonus signals ────────────────────────────────────────────────
    # Visual appeal is a genuine value multiplier — decorative books sell on looks alone.
    # Multiple aesthetic signals stack — a gilt pictorial board book scores higher
    # than a plain cloth book of the same content.
    aesthetic_found = []
    for sig in AESTHETIC_BONUS_SIGNALS:
        if sig.lower() in combined:
            aesthetic_found.append(sig)

    if aesthetic_found:
        # Score +2 for the first aesthetic signal, +1 for each additional
        score += 2 + (len(aesthetic_found) - 1)
        for sig in aesthetic_found:
            signals.append(f"✨ {sig.title()}")

    # ── Priority genre signals (proven profitable) ────────────────────────────
    is_astronomy       = any(g.lower() in combined for g in PRIORITY_GENRE_ASTRONOMY)
    is_natural_history = any(g.lower() in combined for g in PRIORITY_GENRE_NATURAL_HISTORY)
    is_occult          = any(g.lower() in combined for g in PRIORITY_GENRE_OCCULT)

    if is_astronomy:
        score += 3
        signals.append("🔭 PRIORITY genre: Astronomy (+3)")
    if is_natural_history:
        score += 3
        signals.append("🌿 PRIORITY genre: Natural History (+3)")
    if is_occult:
        score += 3
        signals.append("🔮 PRIORITY genre: Occult/Supernatural (+3)")

    # ── Other genre signals ───────────────────────────────────────────────────
    if not is_astronomy and not is_natural_history and not is_occult:
        for genre in TARGET_GENRE_SIGNALS:
            if genre.lower() in combined:
                score += 1
                signals.append(f"📂 {genre.title()}")
                break  # one genre match is enough

    # ── Age signals ───────────────────────────────────────────────────────────
    for sig in AGE_SIGNALS:
        if sig.lower() in combined:
            score += 1
            signals.append(f"📖 {sig.title()}")

    # ── Year hint ─────────────────────────────────────────────────────────────
    year = item.get("year_hint")
    if year:
        # Priority genres get extended cutoff to 1910
        is_priority = (
            any(g.lower() in combined for g in PRIORITY_GENRE_NATURAL_HISTORY) or
            any(g.lower() in combined for g in PRIORITY_GENRE_ASTRONOMY) or
            any(g.lower() in combined for g in PRIORITY_GENRE_OCCULT)
        )
        effective_cutoff = HARD_BLOCK_AFTER_YEAR_PRIORITY if is_priority else HARD_BLOCK_AFTER_YEAR

        if year > effective_cutoff:
            score -= 3
            signals.append(f"🚫 Post-cutoff year ({year})")
        elif YEAR_SWEET_SPOT_START <= year <= YEAR_SWEET_SPOT_END:
            score += 2
            signals.append(f"📅 Sweet spot year: {year}")
        elif year <= effective_cutoff:
            # 1899-1910 for priority genres — still valuable Edwardian
            score += 1
            signals.append(f"📅 Edwardian era: {year}")
        else:
            signals.append(f"📅 Year: {year} (borderline era)")

    # ── Seller unawareness signals ────────────────────────────────────────────
    # Sparse listings are a strong indicator the seller doesn't know the value.
    # These are the listings that consistently produce the best flips.
    title       = (item.get("title") or "")
    description = (item.get("description") or "").strip()
    title_words = len(title.split())
    price       = item.get("price", 999)

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

    # Bundle of old/vintage books — house clearance pattern, high unawareness signal
    bundle_words = {"bundle", "joblot", "lot", "collection", "stack", "pile"}
    age_words    = {"old", "vintage", "antique", "hardback", "hardbacks"}
    title_word_set = set(title.lower().split())
    if bundle_words & title_word_set and age_words & title_word_set:
        score += 2
        signals.append("📦 Bundle of old/vintage books")

    # ── Price bonus ───────────────────────────────────────────────────────────
    if price <= 5.0:
        score += 1
        signals.append("💸 Low price — seller likely unaware of value")

    # ── Favourite count — social proof signal (new listings only) ────────────
    # Only counts if the listing is 40 minutes old or less.
    # 15 favourites in 20 minutes = buyers piling on right now = urgent.
    # 15 favourites on a 3-day-old listing = normal accumulation = not urgent.
    favourites  = int(item.get("favourites", 0) or 0)
    listing_age = item.get("listing_age")  # age in minutes, None if unknown
    is_fresh    = listing_age is not None and listing_age <= 40

    if favourites >= 5 and is_fresh:
        if favourites >= 20:
            score += 3
            signals.append(f"🔥 {favourites} favourites in {listing_age}min — very high interest (+3)")
        elif favourites >= 10:
            score += 2
            signals.append(f"❤️ {favourites} favourites in {listing_age}min — high interest (+2)")
        else:
            score += 1
            signals.append(f"❤️ {favourites} favourites in {listing_age}min — noted interest (+1)")
    # Poetry sells slowly on Vinted — deprioritise unless other strong signals
    SLOW_GENRE_SIGNALS = [
        # Poetry and devotional — slow movers on Vinted
        "poetry", "poems", "poetical", "poetical works",
        "verse", "verses", "sonnets", "ballads",
        "hymns", "hymnal", "psalms",
        "bible", "biblical", "holy bible", "scripture", "scriptures",
        "testament", "gospel", "gospels", "prayer book", "book of common prayer",
        "sermon", "sermons", "devotional", "catechism",
        # Reference — low collector value
        "dictionary", "dictionaries", "encyclopaedia", "encyclopedia",
        "encyclopedic", "lexicon", "glossary", "thesaurus",
        # Craft and hobby topics — low resale value
        "knitting", "crochet", "sewing", "embroidery", "needlework",
        "dressmaking", "clothing book", "clothes book", "fashion book",
        "cookery", "cookbook", "cooking", "recipes", "baking",
        "gardening", "woodwork", "carpentry",
        # Literary fiction — not the target genre
        # Specific phrases only to avoid hitting natural history / exploration titles
        "short stories",
        "collected fiction",
        "complete fiction",
        "classic fiction",
        "romantic fiction",
        "detective fiction",
        "crime fiction",
        "ghost stories",    # only if NOT matched by occult genre signals
        "fairy tales",
        "collected novels",
        "complete novels",
    ]
    # Only apply slow genre penalty if no priority genre matched —
    # a "ghost stories" collection that also hits occult signals should not be penalised.
    if not is_astronomy and not is_natural_history and not is_occult:
        for slow in SLOW_GENRE_SIGNALS:
            if slow.lower() in combined:
                score -= 1
                signals.append(f"🐌 Slow seller: {slow.title()} (-1)")
                break  # one penalty only

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

    # Modern publishers with no Victorian relevance — hard block regardless of score
    MODERN_PUBLISHER_BLOCK = [
        "ladybird",
        "penguin modern",
        "puffin",
        "usborne",
        "dorling kindersley",
        "miles kelly",
        "bloomsbury publishing",
    ]
    MODERN_PUBLISHER_EXACT = [
        "dk eyewitness", "dk publishing", "published by dk",
        "scholastic press", "scholastic books", "scholastic ltd",
        "by scholastic",
    ]
    title_lower = (item.get("title") or "").lower()
    year = item.get("year_hint")
    is_victorian_year = year and year <= 1900
    if not is_victorian_year:
        for pub in MODERN_PUBLISHER_BLOCK:
            if pub in title_lower:
                return True, f"Modern publisher ({pub.title()})"
        for pub in MODERN_PUBLISHER_EXACT:
            if pub in title_lower:
                return True, f"Modern publisher ({pub.title()})"

    # Non-book item (clothing/toy/cosmetic)
    # Use specific multi-word phrases to avoid false matches on book titles
    # e.g. "ring" matches "Lord of the Rings", "dress" matches "address"
    NON_BOOK_ITEM_SIGNALS = [
        "pyjama", "pyjamas", "leggings", "hoodie", "gilet", "joggers",
        "t-shirt", "tshirt", "trousers", "jumpsuit", "cardigan",
        "wellington boots", "wellies",
        "soft toy", "plush toy", "figurine bundle", "polly pocket",
        "hand cream", "face mask", "body lotion", "body butter", "body yoghurt",
        "mascara wands", "lip balm", "deodorant",
        "wax melt", "wax burner",
        "keyring set", "earring set", "necklace set", "bracelet set",
        "plant pot", "ceramic vase",
        # Trainers / footwear — puma ralph sampson lo is a shoe not a book
        "puma ralph sampson", "ralph sampson lo", "ralph sampson low",
        # Clothing size indicators — reliable signals that it's not a book
        "size xl", "size l ", "size m ", "size s ", "size xs",
        "size uk", "size eu", "size us",
        "uk 10)", "uk 12)", "uk 14)", "uk 16)",
        "age 3-", "age 4-", "age 5-", "age 6-", "age 7-",
        "age 8-", "age 9-", "age 10-", "age 11-", "age 12-",
    ]
    title_lower = (item.get("title") or "").lower()
    if any(phrase in title_lower for phrase in NON_BOOK_ITEM_SIGNALS):
        return True, "Non-book item (clothing/toy/cosmetic)"

    # Book accessories and decorative non-books
    # Includes shelf signs, hanging items, club tickets, and branded resin items
    BOOK_ACCESSORY_PHRASES = [
        # Bookends, storage, stands
        "book end", "bookend", "book ends", "bookends",
        "book box", "book shaped", "book nook",
        "book rack", "book riser", "book stand",
        "book safe", "storage box", "trinket box",
        "bookmark", "book mark",
        # Decorative / gift items that are not books
        "shelf sign",
        "wall sign",
        "door sign",
        "hanging sign",
        "book sign",
        "book lover gift",
        "bookish gift",
        "book themed",
        "book lover mug",
        "book lover tote",
        "reading gift",
        # Event / membership items
        "club ticket",
        "book ticket",
        "event ticket",
        # Brand that makes resin/gothic decorative items, not books
        "nemesis now",
    ]
    if any(phrase in title_lower for phrase in BOOK_ACCESSORY_PHRASES):
        return True, "Book accessory (not an actual book)"

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
    has_year       = item.get("year_hint") is not None
    # If a Victorian year is present, it's almost certainly a book listing
    if not has_book_word and not has_genre_word and not has_year:
        return True, "No book/print content indicators found"

    # Post-1900 year in title — priority genres get extended cutoff to 1910
    year = item.get("year_hint")
    if year:
        combined_check = ((item.get("title") or "") + " " + (item.get("description") or "")).lower()
        is_priority = (
            any(g.lower() in combined_check for g in PRIORITY_GENRE_NATURAL_HISTORY) or
            any(g.lower() in combined_check for g in PRIORITY_GENRE_ASTRONOMY) or
            any(g.lower() in combined_check for g in PRIORITY_GENRE_OCCULT)
        )
        effective_cutoff = HARD_BLOCK_AFTER_YEAR_PRIORITY if is_priority else HARD_BLOCK_AFTER_YEAR
        if year > effective_cutoff:
            return True, f"Post-cutoff year detected ({year})"

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