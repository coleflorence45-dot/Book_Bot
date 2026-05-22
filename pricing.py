# pricing.py — Recommended Vinted sell price calculator
#
# Uses eBay sold prices, AbeBooks asking prices, buy price and score
# to suggest what to list a bought book for on Vinted.

def calculate_sell_price(
    buy_price: float,
    ebay: dict,
    abebooks: dict,
    score: int,
) -> dict:
    """
    Returns a dict with:
        recommended_price  (float)  — suggested Vinted listing price
        basis              (str)    — what the recommendation is based on
        estimated_profit   (float)  — profit at recommended price after Vinted ~5% fee
        confidence         (str)    — High / Medium / Low
    """

    VINTED_FEE = 0.05          # Vinted takes ~5% on sales
    VINTED_DISCOUNT = 0.65     # Vinted buyers expect ~35% less than eBay
    ABEBOOKS_DISCOUNT = 0.35   # AbeBooks is inflated — apply heavy discount
    MIN_MULTIPLE = 2.5         # Always aim for at least 2.5x buy price
    MIN_PROFIT = 5.0           # Minimum £5 profit worth listing for

    candidates = []
    basis_parts = []

    # ── eBay sold — most reliable signal ──────────────────────────────────────
    if ebay.get("found") and ebay.get("median_sold", 0) > 0:
        ebay_based = round(ebay["median_sold"] * VINTED_DISCOUNT, 2)
        candidates.append(("ebay", ebay_based))
        basis_parts.append(f"eBay median £{ebay['median_sold']:.0f}")

    # ── AbeBooks asking — secondary signal ────────────────────────────────────
    if abebooks.get("found") and abebooks.get("lowest_price", 0) > 0:
        abe_based = round(abebooks["lowest_price"] * ABEBOOKS_DISCOUNT, 2)
        candidates.append(("abebooks", abe_based))
        basis_parts.append(f"AbeBooks from £{abebooks['lowest_price']:.0f}")

    # ── Score-based multiplier — fallback when no market data ─────────────────
    # Higher score = more confident the book is rare/valuable
    if score >= 9:
        score_multiple = 6.0
    elif score >= 7:
        score_multiple = 4.0
    else:
        score_multiple = 3.0

    score_based = round(buy_price * score_multiple, 2)
    candidates.append(("score", score_based))

    # ── Minimum floor — always at least 2.5x buy price ───────────────────────
    floor = round(buy_price * MIN_MULTIPLE, 2)

    # ── Pick the best estimate ─────────────────────────────────────────────────
    # Prefer eBay, then AbeBooks, then score-based
    # But never go below the floor
    priority_order = ["ebay", "abebooks", "score"]
    raw_price = floor
    winning_basis = "minimum multiple"

    for source in priority_order:
        for name, price in candidates:
            if name == source and price > floor:
                raw_price = price
                winning_basis = source
                break
        if winning_basis == source:
            break

    # Ensure floor
    raw_price = max(raw_price, floor)

    # ── Round to clean Vinted-friendly price ──────────────────────────────────
    if raw_price >= 50:
        recommended = round(raw_price / 5) * 5       # round to nearest £5
    elif raw_price >= 20:
        recommended = round(raw_price / 2) * 2       # round to nearest £2
    else:
        recommended = round(raw_price)               # round to nearest £1

    # Ensure minimum profit makes listing worthwhile
    net_recommended = recommended * (1 - VINTED_FEE)
    estimated_profit = round(net_recommended - buy_price, 2)

    if estimated_profit < MIN_PROFIT:
        recommended = round((buy_price + MIN_PROFIT) / (1 - VINTED_FEE)) + 1

    estimated_profit = round(recommended * (1 - VINTED_FEE) - buy_price, 2)

    # ── Confidence level ──────────────────────────────────────────────────────
    if winning_basis == "ebay" and ebay.get("confirmed_flip"):
        confidence = "High"
    elif winning_basis in ("ebay", "abebooks"):
        confidence = "Medium"
    else:
        confidence = "Low — no market data, based on score"

    # ── Build basis string ────────────────────────────────────────────────────
    if basis_parts:
        basis = " · ".join(basis_parts)
    else:
        basis = f"Score {score} multiplier (no market data found)"

    return {
        "recommended_price": float(recommended),
        "estimated_profit":  estimated_profit,
        "basis":             basis,
        "confidence":        confidence,
    }


def format_price_line(pricing: dict, buy_price: float) -> str:
    """Format the pricing recommendation for a Telegram message."""
    if not pricing:
        return ""

    rec    = pricing["recommended_price"]
    profit = pricing["estimated_profit"]
    conf   = pricing["confidence"]
    basis  = pricing["basis"]

    profit_emoji = "🔥" if profit >= 30 else "💰" if profit >= 15 else "📈"
    conf_emoji   = "✅" if conf == "High" else "🟡" if conf == "Medium" else "⚪"

    return (
        f"{profit_emoji} <b>List for ~£{rec:.0f}</b> "
        f"(est. profit £{profit:.0f} after fees)\n"
        f"{conf_emoji} Confidence: {conf}\n"
        f"📊 Based on: {basis}"
    )