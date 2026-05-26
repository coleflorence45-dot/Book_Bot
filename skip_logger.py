# skip_logger.py — learns why books are being rejected by image analysis
#
# Logs SKIP verdicts with reason, title, score, and price.
# Run analyse_skips() any time to see the top rejection patterns.
# Helps identify systematic issues (e.g. "ex-library" appearing too often,
# or a genre that consistently fails the image check).

import json
import os
from collections import Counter
from datetime import datetime

SKIP_LOG_FILE = "skip_log.json"

# Common words to ignore when analysing reasons
STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "in", "on", "at", "to", "is",
    "it", "this", "with", "from", "for", "not", "no", "as", "are", "has",
    "book", "image", "photo", "visible", "clearly", "likely", "looks",
}


def log_skip(item: dict, verdict: dict):
    """
    Log an image SKIP verdict to skip_log.json.
    Called from main.py whenever image analysis returns SKIP.
    """
    try:
        data = _load()
        data["skips"].append({
            "title":  item.get("title", ""),
            "price":  float(item.get("price", 0)),
            "score":  item.get("score", 0),
            "reason": verdict.get("reason", ""),
            "date":   datetime.now().strftime("%Y-%m-%d"),
        })
        data["total_skips"] += 1
        _save(data)
    except Exception as e:
        print(f"  [skip_logger] Error: {e}")


def analyse_skips(top_n: int = 15) -> str:
    """
    Return a formatted summary of the most common skip reasons.
    Call this from the terminal any time:
        python -c "from skip_logger import analyse_skips; print(analyse_skips())"
    """
    data  = _load()
    skips = data.get("skips", [])
    if not skips:
        return "No skips logged yet."

    total = len(skips)

    # Top reason phrases — extract meaningful words from each reason
    word_counts: Counter = Counter()
    phrase_counts: Counter = Counter()

    for s in skips:
        reason = (s.get("reason") or "").lower()
        # Count individual words
        words = [w for w in reason.replace(",", " ").replace(".", " ").split()
                 if len(w) > 3 and w not in STOPWORDS]
        word_counts.update(words)
        # Count two-word phrases
        for i in range(len(words) - 1):
            phrase_counts.update([f"{words[i]} {words[i+1]}"])

    lines = [
        f"━━━ Skip Analysis ({total} total skips) ━━━",
        "",
        "Top rejection phrases:",
    ]
    for phrase, count in phrase_counts.most_common(top_n):
        pct = round(count / total * 100)
        lines.append(f"  {count:3d}x ({pct:2d}%)  {phrase}")

    lines += ["", "Top rejection words:"]
    for word, count in word_counts.most_common(top_n):
        pct = round(count / total * 100)
        lines.append(f"  {count:3d}x ({pct:2d}%)  {word}")

    # Recent skips
    lines += ["", "Last 5 skips:"]
    for s in reversed(skips[-5:]):
        lines.append(f"  [{s['date']}] £{s['price']:.2f} score={s['score']} — {s['title'][:50]}")
        lines.append(f"           Reason: {s['reason']}")

    return "\n".join(lines)


def _load() -> dict:
    if not os.path.exists(SKIP_LOG_FILE):
        return {"skips": [], "total_skips": 0}
    try:
        with open(SKIP_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"skips": [], "total_skips": 0}


def _save(data: dict):
    with open(SKIP_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)