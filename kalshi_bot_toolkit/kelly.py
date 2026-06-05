"""Kelly-stake math for Kalshi YES contracts — pure and dependency-free.

Buy YES at ``price_c``c: you risk ``c`` and win ``100 - c`` if the market
resolves YES, so the net odds are ``b = (100 - c) / c`` and the full-Kelly
fraction of your bankroll is ``f* = p - q/b`` (with ``q = 1 - p``). A
negative ``f*`` means the price is too high for your probability — don't bet.

Fractional Kelly (1/2 or 1/4) is the practical norm: full Kelly is optimal
only if your probability estimate is exactly right, and a wrong estimate
over-bets toward ruin. This module surfaces that warning instead of hiding
it. Same inputs always give the same output — no IO, no randomness.
"""
from __future__ import annotations

import math


def kelly_stake(bankroll: float, p_pct: float, price_c: int) -> dict:
    """Kelly stake for a Kalshi YES at ``price_c``c given your probability
    estimate ``p_pct``%.

    Args:
        bankroll: account size in dollars (must be > 0).
        p_pct:    your estimated probability the market resolves YES (0-100).
        price_c:  current YES price in cents (1-99).

    Returns ``{"ok": False, "error": ...}`` on invalid input, otherwise a
    dict with the edge, expected value, full/fractional Kelly stakes, and a
    plain-language note.
    """
    if bankroll <= 0 or not (0 <= p_pct <= 100) or not (1 <= price_c <= 99):
        return {"ok": False,
                "error": "bankroll>0, prob 0-100%, price 1-99c"}
    p = p_pct / 100.0
    q = 1.0 - p
    c = price_c / 100.0
    b = (1.0 - c) / c                       # net odds per $1 staked
    f = p - q / b                           # full-Kelly fraction
    ev_cents = round(100 * p - price_c, 2)  # EV per contract, cents
    edge_pct = round((100 * p - price_c) / price_c * 100, 2)
    no_bet = f <= 0

    def growth(frac: float) -> float:
        if frac <= 0 or frac >= 1:
            return 0.0
        return round(p * math.log(1 + frac * b) + q * math.log(1 - frac), 5)

    f_clamped = 0.0 if no_bet else min(f, 1.0)
    return {
        "ok": True,
        "edge_pct": edge_pct,
        "ev_cents": ev_cents,
        "net_odds_b": round(b, 3),
        "kelly_full_pct": round(f_clamped * 100, 2),
        "no_bet": no_bet,
        "stake_full": round(bankroll * f_clamped, 2),
        "stake_half": round(bankroll * f_clamped * 0.5, 2),
        "stake_quarter": round(bankroll * f_clamped * 0.25, 2),
        "growth_full": growth(f_clamped),
        "growth_half": growth(f_clamped * 0.5),
        "note": ("Negative edge at this price — Kelly says DO NOT BET."
                 if no_bet else
                 "Kelly is optimal only if your probability is right; a "
                 "wrong estimate over-bets toward ruin. Fractional Kelly "
                 "(1/2 or 1/4) is the practical norm every bot uses."),
    }
