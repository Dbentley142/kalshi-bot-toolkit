"""Structural field-sum mispricing scanner for Kalshi multi-outcome events.

On a single binary market there is no arbitrage — NO is the exact mirror of
YES. The structural edge lives in the **field** of a mutually-exclusive event.
If *exactly one* of N outcomes resolves YES, then (net of fees):

    Σ(YES_ask) < 100c  -> buy every leg, locking a guaranteed payout  (buy-field)
    Σ(YES_bid) > 100c  -> sell every leg, locking a guaranteed payout  (sell-field)

### The catch — why most "fields under 100c" are NOT free money

Kalshi's `mutually_exclusive` flag means *at most one* YES, **not exactly
one**. If the listed outcomes are not *collectively exhaustive* — e.g. "Who
will be the next Pope?" lists seven cardinals but an unlisted one could win —
then every leg can resolve NO, and a low `Σ(YES_ask)` is just missing-outcome
risk, not arbitrage. This scanner reports the sums and flags **candidates**; it
does **not** promise free money. Always verify the field is exhaustive and
liquid at the quoted size before trusting a flag.

Fees come from :mod:`kalshi_bot_toolkit.fees`, so the edge can never drift from
what a trade actually costs. Pure and deterministic.
"""
from __future__ import annotations

from .fees import calculate_fee


def _fee(price_cents: int) -> int:
    return int(calculate_fee(price_cents=price_cents, count=1, is_maker=False))


def field_scan(legs: list, *, mutually_exclusive: bool) -> dict | None:
    """Field-sum mispricing for one event.

    Args:
        legs: the event's markets, each a dict with integer-cent ``yes_ask`` /
            ``yes_bid`` (as produced by ``normalize_market``).
        mutually_exclusive: the event's flag — a ``candidate`` is only flagged
            when this is True.

    Returns None for non-fields (<2 legs), else a dict with the field sums,
    fee-aware ``buy_edge`` / ``sell_edge``, a caveated ``candidate``, and a
    ``caveat`` string.
    """
    if len(legs) < 2:
        return None

    asks = [l["yes_ask"] for l in legs if l.get("yes_ask")]
    bids = [l["yes_bid"] for l in legs if l.get("yes_bid")]
    complete = len(asks) == len(legs) and len(bids) == len(legs)

    sum_ask = round(sum(asks), 1) if asks else None
    sum_bid = round(sum(bids), 1) if bids else None
    buy_fee = sum(_fee(l["yes_ask"]) for l in legs if l.get("yes_ask"))
    sell_fee = sum(_fee(l["yes_bid"]) for l in legs if l.get("yes_bid"))

    buy_edge = (round(100.0 - sum_ask - buy_fee, 1)
                if complete and sum_ask is not None else None)
    sell_edge = (round(sum_bid - 100.0 - sell_fee, 1)
                 if sum_bid is not None else None)

    candidate = None
    if mutually_exclusive:
        if buy_edge is not None and buy_edge > 0:
            candidate = "buy-field"
        elif sell_edge is not None and sell_edge > 0:
            candidate = "sell-field"

    return {
        "legs": len(legs),
        "mutually_exclusive": mutually_exclusive,
        "sum_yes_ask": sum_ask,
        "sum_yes_bid": sum_bid,
        "buy_edge": buy_edge,    # cents of guaranteed profit IF exhaustive
        "sell_edge": sell_edge,
        "candidate": candidate,  # "buy-field" | "sell-field" | None
        "complete": complete,    # were all legs quoted on both sides?
        "caveat": ("Candidate only if the field is collectively exhaustive "
                   "(no unlisted outcome) AND liquid at the quoted size. "
                   "Mutually-exclusive != exhaustive. Verify before trading."),
    }


def scan_events(events: list) -> list:
    """Field-scan a list of event dicts (each with ``markets`` and
    ``mutually_exclusive``). Returns scans that flagged a candidate, with the
    biggest edge first."""
    found = []
    for e in events:
        scan = field_scan(e.get("markets") or [],
                          mutually_exclusive=bool(e.get("mutually_exclusive")))
        if scan and scan["candidate"]:
            scan["event_ticker"] = e.get("event_ticker")
            scan["title"] = e.get("title")
            found.append(scan)
    found.sort(key=lambda s: max(s["buy_edge"] or 0, s["sell_edge"] or 0),
               reverse=True)
    return found
