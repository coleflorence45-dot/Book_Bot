# scorer.py — Age & value signal scorer (Books Bot)
# Tuned for Victorian first editions 1860–1898

import re
import unicodedata

from config import (
    AGE_SIGNALS,
    ILLUSTRATION_BONUS_SIGNALS,
    AESTHETIC_BONUS_SIGNALS,
    PUBLISHER_SIGNALS,
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
    # Binding types — "Leatherbound Classics", "leather bound diary" etc.
    "leatherbound", "leather bound", "leather-bound", "leather binding",
    "cloth bound", "cloth-bound", "vellum", "morocco", "calf", "calfskin",
    "gilt", "gilded",
    "receipts", "workshop", "mechanics", "manufacture", "manufactures",
    "treatise on", "principles of", "elements of", "theory of",
    "history of", "lives of", "life of", "memoirs of", "narrative of",
    "account of", "description of", "guide to", "introduction to",
    "recollections", "reminiscences", "autobiography", "biography",
    "sermons", "lectures", "poems", "poetry", "poetical", "prose",
    "dramas", "plays", "novels", "tales", "legends", "mythology",
    "writings", "writing of", "writings of",   # e.g. "Life and writings of Charlotte Brontë"
    "works of", "works by", "selected works", "complete works", "collected works",
]


# Words that — when found in the title — indicate a standalone print, not a book.
# Using word-boundary sets avoids Unicode dash / separator issues entirely.
PRINT_TITLE_NOUNS = {"print", "prints", "engraving", "engravings"}

# A listing matching a print noun is still OK if it clearly IS a book.
STRONG_BOOK_WORDS = {
    "volume", "hardback", "hardcover",
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

    # ── Publisher match ────────────────────────────────────────────────────────
    for pub in PUBLISHER_SIGNALS:
        if pub.lower() in combined:
            score += 2
            signals.append(f"🏛️ Publisher: {pub.title()}")
            break

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
        # Modern serialised novels/comics — "#2", "book 3" etc. signals modern series
        "# 2", "# 3", "# 4", "#2", "#3", "#4", "#5",
        "book 2 ", "book 3 ", "book 4 ", "book 5 ",
        # Specific phrases only to avoid hitting natural history / exploration titles
        "short stories",
        "collected fiction",
        "complete fiction",
        "classic fiction",
        "romantic fiction",
        "detective fiction",
        "crime fiction",
        "ghost stories",
        "fairy tales",
        "collected novels",
        "complete novels",
        # Equestrian / sport / leisure — modern, low collector value
        "horse riding", "horse book", "riding book",
        "equestrian", "show jumping",
        "walking book", "hiking book", "rambling book",
        "fishing book", "angling book",
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

    def _normalise(text: str) -> str:
        """Strip accents so Pokémon→pokemon, Astérix→asterix, etc."""
        return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("ascii").lower()

    title_lower         = _normalise(item.get("title") or "")
    title_lower_unicode = (item.get("title") or "").lower()  # keep original for phrases that don't need it

    # Individual pages or cuttings sold from books — not a complete book
    CUTTING_PHRASES = [
        "cutting from book", "cut from book",
        "page from book", "pages from book",
        "taken from book", "removed from book",
        "from a book", "from an old book",
        "book plate", "book-plate", "bookplate",
    ]
    if any(phrase in title_lower for phrase in CUTTING_PHRASES):
        return True, "Individual page/cutting from a book (not a complete book)"

    # Modern publishers with no Victorian relevance — hard block regardless of score
    MODERN_PUBLISHER_BLOCK = [
        "ladybird", "lady bird",    # spaced variant bypasses the original
        "corgi books", "corgi classics",   # Corgi Books founded 1951
        "penguin modern",
        "puffin",
        "usborne",
        "dorling kindersley",
        "miles kelly",
        "bloomsbury publishing",
        "folio society",    # modern reprint publisher est. 1947 — never original
        "wordsworth editions",  # cheap modern reprints of classics
        "wordsworth classics",
        "collector's library",  # modern gift editions
        "flame tree publishing",
        "canterbury classics",
        "priory classics",
        "dennis wheatley library",
        "time-life books", "time life books",   # modern illustrated series
    ]
    MODERN_PUBLISHER_EXACT = [
        "dk eyewitness", "dk publishing", "published by dk",
        "scholastic press", "scholastic books", "scholastic ltd",
        "by scholastic",
    ]
    title_lower = _normalise(item.get("title") or "")
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
        # Clothing and accessories — not books
        "puma ralph sampson", "ralph sampson lo", "ralph sampson low",
        "scarf", "scarves", "shawl", "wrap",
        # Clothing size indicators
        "size xl", "size l ", "size m ", "size s ", "size xs",
        "size uk", "size eu", "size us",
        "uk 10)", "uk 12)", "uk 14)", "uk 16)",
        "age 3-", "age 4-", "age 5-", "age 6-", "age 7-",
        "age 8-", "age 9-", "age 10-", "age 11-", "age 12-",
        # Occult non-book items — score on genre signals but are not books
        "spell candle", "spell candles",
        "smudge stick", "sage stick", "incense stick", "incense box",
        "incense cone", "incense cones", "backflow cone",
        "pendulum cloth", "divination cloth", "tarot cloth",
        "pendulum board", "ouija board",
        "trinket dish", "crystal set",
        "tarot card box", "tarot deck",
        "moon pentagram", "altar cloth",
        "smudging bowl", "wax melt burner",
        "wooden ornament", "wood ornament",
        "wall plaque", "wood plaque",
        "mushroom sign", "witch sign", "magic sign",
        "witchy ornament", "witchy decor",
        "rune pick", "rune set",
        # Physical product kits — score on genre signals (magic/occult/nature)
        # but are toys or activity sets, not books
        "magician kit", "magic kit", "magic set",
        "science kit", "experiment kit",
        "activity kit", "craft kit", "sewing kit",
        "bug kit", "nature kit", "fossil kit",
        "astronomy kit", "telescope kit", "microscope kit",
        # Comic strips and cartoon books — not collectible Victorian books
        "comic strip", "comic strips",
        "comic book lot", "comic lot", "comic bundle",
        "garfield", "peanuts snoopy", "asterix",
        "beano annual", "dandy annual",
        # Modern comic publishers
        "vertigo comics", "dark horse comics", "image comics",
        "idw comics", "boom studios",
        # Modern franchises — never Victorian
        "transformers", "disney", "my little pony",
        "captain underpants", "diary of a wimpy kid",
        "percy jackson", "star wars", "star trek",
        "return of the jedi", "a new hope", "the empire strikes back",
        "famous five", "secret seven", "magic faraway tree",
        "mr men", "mr. men", "little miss",
        "lego", "pokemon", "minecraft",
        "x-men", "x men", "avengers", "simpsons",
        "chronicles of narnia", "narnia",
        "doctor who", "dr who",
        "game of thrones",
        "lord of the rings", "lotr",    # Tolkien franchise
        "tolkien", "the hobbit",         # Tolkien — published 1937 onwards
        "dr seuss", "dr. seuss",         # Modern children's author
        "trudi canavan",                # Modern fantasy author
        "greg bear",                    # Modern sci-fi — "Eternity", "Eon" etc.
        "terry pratchett", "pratchett", # Discworld — 1983 onwards
        "terry brooks",                 # Shannara series — 1977 onwards
        "graham greene", "brighton rock",  # Greene 1904–1991 — keeps recurring
        "y2k",                          # Year 2000 — no Victorian book is Y2K
        "hairy maclary", "hairy mclary",
        "to kill a mockingbird",
        "to kill a mocking bird",   # spaced variant bypassed the original
        "the woman in black",        # Susan Hill 1983 — consistently scores 9 on ghost signals
        "hunkydory",                 # craft paper/die-cut brand, not a book
        # Modern authors whose titles repeatedly score on Victorian genre signals
        "murakami",         # Haruki Murakami — "bird" in titles triggers natural history
        "stephen king",     # horror genre signals inflate score
        "james patterson",  # thriller, recurs in scans
        "jodi picoult",
        "john grisham",
        "lee child",
        "reacher",          # Lee Child series
        "harlan coben",
        # Book club tickets / modern reader subscriptions
        "book club ticket", "book club box",
        "bookish box", "book box subscription",
        "smut era", "thriller era", "vampire era",
        "cowboy romance book club", "spicy romance book club",
        # Subscription box merchandise brands
        "fairyloot", "fairy loot",
        "illumicrate", "owlcrate", "owl crate",
    ]
    title_lower = _normalise(item.get("title") or "")
    if any(phrase in title_lower for phrase in NON_BOOK_ITEM_SIGNALS):
        return True, "Non-book item (clothing/toy/cosmetic)"

    # ── Religious / devotional content — hard block ───────────────────────────
    # Victorian religious books are common, low-value and slow to sell.
    # Hard block saves both API calls and alert noise.
    RELIGIOUS_PHRASES = [
        "prayer book", "prayer books", "book of prayers",
        "holy bible", "the bible", "king james bible", "kjv bible",
        "new testament", "old testament",
        "book of common prayer",
        "hymn book", "hymnal", "hymnary",
        "psalms", "psalm book",
        "catechism", "devotional", "devotions",
        "sermons", "sermon book",
        "religious tract", "religious text",
        "missal", "breviary", "book of hours",
        "bible stories", "bible story", "bible tales",
        "bible for children", "children's bible", "childrens bible",
        "scripture stories", "sunday school",
        # Theology and divinity — slow sellers regardless of age or condition
        "theology", "theological",
        "divinity", "divine",
        "church history", "ecclesiastical",
        "christian doctrine", "christian faith",
        "commentary on", "biblical commentary",
        "epistle to the", "gospel of",
        "systematic theology", "moral theology",
        "patristic", "patristics",
        "homiletics", "homily",
    ]
    if any(phrase in title_lower for phrase in RELIGIOUS_PHRASES):
        return True, "Religious/devotional book (low resale value)"

    # ── Children's books — hard block ────────────────────────────────────────
    # Modern age-targeted children's titles score heavily on unawareness signals
    # (short title, no description, no publisher) despite being worthless for resale.
    CHILDRENS_BOOK_PHRASES = [
        "bedtime stories",
        "bedtime story",
        "year olds",            # "stories for 6 year olds", "books for 8 year olds"
        "years old book",       # "I'm Three Years Old Book", "I am 5 Years Old Book"
        "i'm one", "i'm two", "i'm three", "i'm four", "i'm five",
        "i am one", "i am two", "i am three", "i am four", "i am five",
        "for toddlers",
        "for babies",
        "baby book",
        "baby books",
        "picture book",
        "picture books",
        "board book",
        "board books",
        "early reader",
        "beginning reader",
        "read aloud",
        "read-aloud",
        "children's reader",
        "childrens reader",
        "ages 3", "ages 4", "ages 5", "ages 6",
        "ages 7", "ages 8", "ages 9", "ages 10",
        "ages 11", "ages 12",
    ]
    if any(phrase in title_lower for phrase in CHILDRENS_BOOK_PHRASES):
        return True, "Children's/age-targeted book (not a collectible)"

    # ── Stationery / blank notebooks — hard block ────────────────────────────
    # Stationery masquerades as books on vague keyword searches.
    STATIONERY_PHRASES = [
        "note book", "note books", "notebook", "notebooks",
        "notepad", "notepads",
        "jotter", "jotters",
        "sketchbook", "sketch book", "sketch pad",
        "exercise book", "exercise books",
        "blank journal", "lined journal", "dot journal",
        "bullet journal", "gratitude journal", "fitness journal",
        "planner book",
    ]
    if any(phrase in title_lower for phrase in STATIONERY_PHRASES):
        return True, "Stationery/blank notebook (not a collectible book)"

    # ── Modern self-help / parenting / lifestyle — hard block ─────────────────
    # These score on "book", "old", "vintage" etc. but are never Victorian.
    MODERN_CONTENT_PHRASES = [
        "gentle sleep", "sleep training", "baby sleep",
        "mindfulness", "self-help", "self help",
        "affirmations", "manifestation",
        "colouring book", "coloring book", "adult colouring", "adult coloring",
        "activity book", "puzzle book", "quiz book",
        "spot the difference", "spot the dog", "spot the cat",
        "hidden pictures", "seek and find", "search and find",
        "word search", "wordsearch", "crossword book",
        "sudoku", "kakuro", "brain teaser",
        "wellness journal", "habit tracker",
        "weight loss", "slimming", "diet book",
        "parenting book", "baby book", "pregnancy book",
        "parenting books", "parenting help", "baby books",
        # Modern wellness/spirituality titles
        "witch wound", "divine feminine", "reclaim your magic",
        "step into your power", "heal your", "shadow work",
        "inner child", "trauma healing",
        "good vibes", "good life book", "positive vibes",
        # TV and media tie-ins — never Victorian
        "coffee table book", "coffee-table book",  # modern large-format genre
        "tv book", "tv collection", "tv tie-in", "tv tie in",
        "bbc book", "itv book",
        "television book", "television collection",
        # Modern reference/price guide publishers
        "miller's antiques", "miller's pocket",
        "miller's collectables", "millers antiques",
        # Fashion and style books — modern, not Victorian collectibles
        "fashion hardback", "fashion book",
        "style book", "vogue on ",
        # Appliance / product instruction books
        "instruction book", "instruction manual",
        "user manual", "user guide",
        "owners manual", "owner's manual",
        "kenwood", "kitchenaid", "thermomix",
        # Modern astrology/horoscope products — score heavily on occult signals
        "horoscope book", "birth chart", "astrology report",
        "personal horoscope", "star sign book",
        # Modern book club subscriptions
        "fantasy era book club", "fantasy era bookclub",
        # Textbooks — educational, not collectible
        "textbook", "text book", "revision guide",
        "gcse", "a-level", "a level", "as level", "as-level",
        "key stage",
        # Victorian school primer titles — "Designed for the Use of Schools"
        # is a Victorian textbook formula that burns API calls on high year scores
        "for the use of schools", "designed for schools",
        "school primer", "school reader", "school arithmetic",
        "school geography", "school grammar", "school history",
        "for the use of classes",
        # Business/accounting textbooks
        "auditing book", "accounting book", "accounting textbook",
        "business studies", "economics textbook",
        "grammar book", "grammar guide",
        # Autobiographies of living/modern people — rarely Victorian
        # Only block clearly modern phrases, not generic "memoir" which
        # could appear on Victorian travel memoirs
        "autobiography", "my autobiography",
        "my story", "my life story",
        # Modern retail/publishing signals
        "waterstones exclusive", "waterstones signed", "signed exclusive",
        "sprayed edges",    # modern special edition feature
        # Photography books — modern, never Victorian collectibles
        "wildlife photography", "nature photography", "photography book",
        "photography saving", "one frame at a time",
    ]
    if any(phrase in title_lower for phrase in MODERN_CONTENT_PHRASES):
        return True, "Modern self-help/lifestyle book (not a collectible)"

    # ── Gardening books — hard block ──────────────────────────────────────────
    # Gardening titles consistently score on unawareness signals without any
    # Victorian content. Hard block avoids log noise and wasted scoring.
    # Note: "botanical", "flora", "natural history" are NOT blocked here —
    # those are handled as priority genres and are valuable.
    GARDENING_PHRASES = [
        "gardening book", "gardening books",
        "garden book", "garden books",
        "vegetable gardening", "flower gardening",
        "allotment book", "allotment guide",
        "grow your own",
    ]
    if any(phrase in title_lower for phrase in GARDENING_PHRASES):
        return True, "Gardening book (not a collectible)"

    # ── Cake / baking / decorating — hard block ───────────────────────────────
    CAKE_PHRASES = [
        "cake decorating", "cake book", "cake baking",
        "cakes for", "cake for",          # catches "enchanted cakes for children"
        "decorated cakes", "celebration cakes", "novelty cakes",
        "sugarcraft", "sugar craft", "cupcake decorating",
        "icing book", "baking book", "baking books",
    ]
    if any(phrase in title_lower for phrase in CAKE_PHRASES):
        return True, "Cake/baking book (not a collectible)"

    # ── DVDs, VHS, video games — hard block ───────────────────────────────────
    # These score on "vintage", "illustrated", "old" etc. but are never books.
    MEDIA_PHRASES = [
        "dvd", "dvds", "vhs", "blu-ray", "blu ray",
        "video game", "playstation", "nintendo", "xbox",
        "strategy guide", "cheat code", "walkthrough guide",
        "gaming guide", "game guide",
    ]
    if any(phrase in title_lower for phrase in MEDIA_PHRASES):
        return True, "Non-book media item (DVD/VHS/game)"

    # ── Single prints described as "book print" ───────────────────────────────
    # Sellers list Victorian-dated prints torn from books with "1894 book print"
    # etc. in the title. These score highly on year + illustration signals but
    # are single pages, not books. Hard block on the phrase alone.
    BOOK_PRINT_PHRASES = [
        "book print", "book plate print", "vintage print",
        "antique print", "old print",
        "botanical print", "natural history print",
        "framed print", "mounted print",
        "illustration print", "engraving print",
        "book plate", "bookplate",      # loose plate torn from a book
        "book of birds plate", "birds plate",
        "vol 1 plate", "vol 2 plate", "volume 1 plate", "volume 2 plate",
    ]
    if any(phrase in title_lower for phrase in BOOK_PRINT_PHRASES):
        return True, "Single print/illustration (not a book)"

    # ── Craft / hobby books — hard block ──────────────────────────────────────
    CRAFT_PHRASES = [
        "decorative effects",    # modern home decor/craft book genre
        "paint effects",         # same genre
        "faux effects",
        "crochet",                         # catches "crochet stitches", "crochet book" etc.
        "crocheting pattern",
        "knitting pattern", "knitting book", "knitting patterns",
        "knits book", "knits for",
        "pop up book", "pop-up book", "pop up noddy", "pop up story",
        "cross stitch", "cross-stitch",
        "needlework book", "embroidery book",
        "sewing book", "sewing pattern", "quilting book",
        "patchwork", "patchwork book",
        "craft book", "craft pattern", "book of crafts", "book of craft",
        "arts and crafts book", "crafts book bundle", "craft book bundle",
        "handmade at home", "hand made at home",
        "candle making", "candlemaking", "candle book", "candlemaker",
        "soap making", "soapmaking",
        "decoupage", "papercrafts", "card making",
        "homemade gifts", "home made gifts",
        "gift making", "gift wrapping",
    ]
    if any(phrase in title_lower for phrase in CRAFT_PHRASES):
        return True, "Craft/hobby book (not a collectible)"

    # ── Music books — hard block ──────────────────────────────────────────────
    MUSIC_PHRASES = [
        "piano book", "piano method", "piano tutor",
        "guitar book", "guitar method", "guitar tutor",
        "organ music", "organ book", "organ pieces", "organ works",
        "sheet music", "music score", "song book", "songbook",
        "chord book", "music theory book",
        "john thompson",   # specific piano method series
    ]
    if any(phrase in title_lower for phrase in MUSIC_PHRASES):
        return True, "Music book (not a collectible)"

    # ── Jewellery/badge/brooch items — hard block ────────────────────────────
    # These score on "vintage" + "book" but are physical accessories
    JEWELLERY_PHRASES = [
        "badge brooch", "brooch badge",
        "pin badge", "enamel badge", "enamel pin",
        "book brooch", "book necklace", "book charm",
        "book locket", "book pendant",
    ]
    if any(phrase in title_lower for phrase in JEWELLERY_PHRASES):
        return True, "Jewellery/accessory item (not a book)"

    # ── Specific modern series — hard block ───────────────────────────────────
    # These series consistently score on signals but are never Victorian.
    MODERN_SERIES_PHRASES = [
        # Reader's Digest — 1950s onward mass-market series
        "reader's digest", "readers digest", "reader's digest",
        # Observer's Books — 1960s-80s Warne/Penguin pocket series
        "observers book", "observer's book",
        "the observers book", "the observer's book",
        # Osprey — modern military history publisher, despite historical dates in titles
        "osprey campaign", "osprey military", "osprey publishing",
        "osprey aviation", "osprey men-at-arms", "osprey warrior",
        "osprey new vanguard", "osprey elite",
        # Magazine collections — not books
        "train magazine", "railway magazine",
        "magazine book", "magazine bundle", "magazine collection",
        "magazine annual",
        # Modern transport history — score on "illustrated" + "history" signals
        "british steam", "steam locomotive", "steam locomotives",
        "railway history", "history of steam",
        "history of the railway", "history of trains",
        # but are never Victorian collectibles worth buying
        "history of aircraft", "history of aviation", "history of flight",
        "history of cars", "history of the car", "history of motoring",
        "history of trains", "history of railways", "history of the railway",
        "history of ships", "history of the titanic", "titanic",
        "slot machine", "slot machines", "fruit machine",
        "history of photography", "history of cinema", "history of film",
        "history of football", "history of cricket", "history of rugby",
        # Children's TV franchises — never Victorian
        "sesame street", "elmo",            # Sesame Street franchise (1969–)
        "ren & stimpy", "ren and stimpy",   # Nickelodeon comic/magazine (1992–)
        # Disney Twisted Tales series — modern YA franchise novels
        "as old as time",                   # Twisted Tales: Beauty & the Beast tie-in
        "mirror mirror twisted",
        "go the distance",                  # Twisted Tales: Hercules
        # Sticker / activity / novelty books
        "sticker book", "sticker activity",
        "matte sticker", "gloss sticker",  # art/merch stickers sold as collectibles
        "iron-on", "sew-on patch", "embroidered patch",  # garment accessories
        # Children's fantasy phrases that stack occult/genre signals
        "magic spell", "spell book for kids", "unicorn magic",
        "my secret unicorn", "rainbow magic",  # named modern children's series
        "santas special letter", "santa's special letter",  # personalised modern Christmas book
        "letter from santa", "letter from father christmas",
        "press out", "press-out",
        # Annuals — almost always post-1900
        "annual 19", "annual 20",
    ]
    if any(phrase in title_lower for phrase in MODERN_SERIES_PHRASES):
        return True, "Modern series/annual (not a collectible)"

    # ── Cookbooks and recipe books — hard block ───────────────────────────────
    COOKBOOK_PHRASES = [
        "cookbook", "cook book", "cookbooks", "cook books",
        "recipe book", "recipe books", "recipes book",
        "baking book", "baking books",
        "cook express", "cooking book",
        "teatime recipes", "tea time recipes",
    ]
    if any(phrase in title_lower for phrase in COOKBOOK_PHRASES):
        return True, "Cookbook/recipe book (not a collectible)"

    # ── Loose book pages / paper — hard block ────────────────────────────────
    LOOSE_PAGES_PHRASES = [
        "book pages", "book paper", "vintage pages",
        "loose pages", "antique pages",
        "book leaves", "book leaf",
    ]
    if any(phrase in title_lower for phrase in LOOSE_PAGES_PHRASES):
        return True, "Loose book pages (not a complete book)"

    # ── Book accessories, decorative non-books, book-shaped homewares ─────────
    BOOK_ACCESSORY_PHRASES = [
        # Bookends, storage, stands
        "book end", "bookend", "book ends", "bookends",
        "book box", "book shaped", "book nook",
        "book rack", "book riser", "book stand",
        "book safe", "storage box", "trinket box",
        "book storage",           # e.g. "book storage unit", "vintage book storage"
        "bookshelf stand", "bookshelf unit", "book shelf stand",
        "bookmark", "book mark",
        # Metal/tin signs — score on "vintage" + "book" + "floral" etc.
        "metal sign", "tin sign", "metal plaque", "tin plaque",
        "30x30cm", "20x30cm", "40x30cm",   # standard sign dimensions in titles
        "book sign", "reader sign", "reading sign",
        "bookcase decor", "bookcase sign",
        "bookshelf decor", "bookshelf sign",
        "library sign", "library decor",
        "wooden sign", "wooden wall sign",
        "sign new",
        "sign boxed",
        # Book-shaped homewares
        "book teapot", "book vase", "book mug", "book pot",
        "book shaped vase", "book shaped teapot",
        "booked shaped",   # common seller typo
        "book holder", "magazine holder", "magazine rack",
        "book stack", "wood book", "wooden book stack",
        # Photo frames and albums — score on "vintage" + "floral" etc.
        "photo frame", "photo album", "folding frame",
        "accordion album", "accordion photo",
        "picture frame",
        # Gift / decorative items
        "book lover gift", "bookish gift", "book themed",
        "book lover mug", "book lover tote",
        "reading gift", "book gift",
        # Event / membership
        "club ticket", "book ticket", "event ticket",
        "book club ticket", "book club box", "book club subscription",
        "romance era bookclub", "spicy book club", "dark romance book club",
        "bookish subscription",
        # Brand that makes resin/gothic decorative items
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

    # "20th century" in title — no Victorian book could reference the 20th century
    # BUT "early 20th century" means the edition/copy is Edwardian-era — do not block
    if "20th century" in title_lower or "twentieth century" in title_lower:
        if "early 20th century" not in title_lower and "early twentieth century" not in title_lower:
            return True, "Post-Victorian subject matter (20th century)"

    # ── ISBN detected — cannot be a Victorian antique ─────────────────────────
    # The ISBN system launched in 1970. Any listing with a clearly real ISBN
    # is post-1970 by definition. However Vinted forces sellers to enter an ISBN
    # even for antiques, so they type zeros, random numbers etc.
    # Rule: only block when obviously real. When in doubt, pass through.
    #
    # Two sources checked:
    #   1. Dedicated isbn field from Vinted API (if returned)
    #   2. Title + description text (seller may have typed it manually)
    combined_full = (
        (item.get("title") or "") + " " + (item.get("description") or "")
    ).lower()

    NO_ISBN_PHRASES = (
        "no isbn", "no isbn number", "no isbn no", "without isbn",
        "doesn't have an isbn", "does not have an isbn",
        "pre-isbn", "pre isbn", "predates isbn",
        "published before isbn", "before isbn",
    )
    negated = any(phrase in combined_full for phrase in NO_ISBN_PHRASES)

    def _is_real_isbn(value: str) -> bool:
        """Return True only if this looks like a genuine ISBN, not a placeholder."""
        digits = re.sub(r'[\s\-]', '', value)
        if len(digits) not in (10, 13):
            return False
        if len(set(digits)) == 1:          # all same digit: 0000000000000
            return False
        if re.match(r'^97[89]0+$', digits):  # 9780000000000
            return False
        if digits in "01234567890123456789":  # sequential run
            return False
        # Must start with 978/979 for ISBN-13, or be 10 digits for ISBN-10
        if len(digits) == 13 and not digits.startswith(('978', '979')):
            return False
        return True

    if not negated:
        # Check dedicated ISBN field from Vinted API
        isbn_field = str(item.get("isbn") or "").strip()
        if isbn_field and _is_real_isbn(isbn_field):
            return True, "ISBN field present (post-1970 book)"

        # Check title + description for isbn keyword + number together
        isbn_with_number = re.search(
            r'\bisbn[\s:\-]*(97[89][\d\-\s]{10,17})\b', combined_full
        )
        if isbn_with_number and _is_real_isbn(isbn_with_number.group(1)):
            return True, "ISBN present (post-1970 book)"

    # ── Brand new items — BNWT / BNW / brand new = cannot be a Victorian antique
    if any(phrase in title_lower for phrase in ("bnwt", "bnwob", "brand new with tags", "brand new unworn")):
        return True, "Brand new item (not an antique)"

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