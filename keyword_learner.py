# keyword_learner.py — learns which words appear in profitable listings
# Analyses BUY alert titles over time and suggests new keywords

import json
import os
import re
from collections import Counter

LEARNED_FILE = "learned_keywords.json"

# Common words to ignore when analysing titles
STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "in", "on", "at", "to", "by",
    "for", "with", "from", "is", "it", "its", "this", "that", "was",
    "old", "book", "books", "vintage", "antique", "hardback", "hardcover",
    "very", "good", "great", "rare", "nice", "beautiful", "lovely",
    "edition", "copy", "volume", "lot", "bundle", "set", "collection",
}


def learn_from_alert(item: dict):
    """Extract meaningful words from a BUY alert title and log their frequency."""
    title = (item.get("title") or "").lower()
    words = re.findall(r'\b[a-z]{4,}\b', title)
    meaningful = [w for w in words if w not in STOPWORDS]

    data = _load()
    for word in meaningful:
        data["word_counts"][word] = data["word_counts"].get(word, 0) + 1
    data["total_buy_alerts"] += 1
    _save(data)


def get_suggestions(min_count: int = 3) -> list:
    """
    Return words that appear in BUY titles frequently enough to be
    worth adding as search keywords.
    """
    data  = _load()
    words = data.get("word_counts", {})
    return sorted(
        [(w, c) for w, c in words.items() if c >= min_count],
        key=lambda x: x[1], reverse=True
    )


def _load() -> dict:
    if not os.path.exists(LEARNED_FILE):
        return {"word_counts": {}, "total_buy_alerts": 0}
    try:
        with open(LEARNED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"word_counts": {}, "total_buy_alerts": 0}


def _save(data: dict):
    with open(LEARNED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)