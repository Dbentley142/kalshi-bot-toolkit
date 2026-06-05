"""Read-only client for Kalshi's public market API — no API key required.

Kalshi serves market data at ``https://api.elections.kalshi.com/trade-api/v2``
without authentication, so the research half of a trading bot needs no
credentials. This client uses only the Python standard library.

Kalshi returns prices in a string ``*_dollars`` / ``*_fp`` schema, e.g.
``yes_ask_dollars = "0.6200"`` and ``volume_fp = "201.67"``. This client
parses those into integer **cents** and attaches clean keys
(``yes_ask``, ``yes_bid``, ``no_ask``, ``no_bid``, ``last_price``,
``volume``, ``open_interest``) onto every market, so your bot code stays
simple and keeps working if Kalshi renames a raw field. The raw keys are
preserved alongside the parsed ones.

Markets are grouped under a **series** (e.g. ``KXBTCD`` = Bitcoin daily).
Filtering by ``series_ticker`` is the reliable way to list a group; a global
title scan can miss markets buried under large categories.

Placing orders requires a signed API key and is intentionally out of scope —
this toolkit is for research and signal math, not execution. Prices are in
cents (1-99).
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Optional

_BASE = "https://api.elections.kalshi.com/trade-api/v2"

# Raw "0.6200" dollar strings -> integer cents.
_CENT_FIELDS = {
    "yes_ask": "yes_ask_dollars",
    "yes_bid": "yes_bid_dollars",
    "no_ask": "no_ask_dollars",
    "no_bid": "no_bid_dollars",
    "last_price": "last_price_dollars",
}
# Raw "201.67" fixed-point strings -> float.
_NUM_FIELDS = {
    "volume": "volume_fp",
    "volume_24h": "volume_24h_fp",
    "open_interest": "open_interest_fp",
    "yes_ask_size": "yes_ask_size_fp",
    "yes_bid_size": "yes_bid_size_fp",
}


def _cents(dollar_str) -> Optional[int]:
    if dollar_str in (None, ""):
        return None
    try:
        return round(float(dollar_str) * 100)
    except (TypeError, ValueError):
        return None


def _num(fp_str) -> Optional[float]:
    if fp_str in (None, ""):
        return None
    try:
        return float(fp_str)
    except (TypeError, ValueError):
        return None


def normalize_market(raw: dict) -> dict:
    """Copy a raw Kalshi market dict with clean cent/number keys attached.

    Adds integer-cent ``yes_ask`` / ``yes_bid`` / ``no_ask`` / ``no_bid`` /
    ``last_price`` and numeric ``volume`` / ``volume_24h`` / ``open_interest``,
    parsed from the raw ``*_dollars`` / ``*_fp`` strings. Raw keys are kept.
    """
    m = dict(raw)
    for clean, rk in _CENT_FIELDS.items():
        m[clean] = _cents(raw.get(rk))
    for clean, rk in _NUM_FIELDS.items():
        m[clean] = _num(raw.get(rk))
    return m


class KalshiPublicClient:
    """Thin, dependency-free reader for Kalshi's public endpoints."""

    def __init__(self, base_url: str = _BASE, timeout: float = 10.0,
                 user_agent: str = "kalshi-bot-toolkit") -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        url = f"{self.base_url}/{path}"
        if params:
            clean = {k: v for k, v in params.items() if v is not None}
            if clean:
                url = f"{url}?{urllib.parse.urlencode(clean)}"
        req = urllib.request.Request(
            url, headers={"User-Agent": self.user_agent,
                          "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def get_market(self, ticker: str) -> dict:
        """One market by ticker, with parsed ``yes_ask`` / ``last_price`` /
        ``volume`` (etc.) attached."""
        return normalize_market(self._get(f"markets/{ticker}")["market"])

    def list_markets(self, *, status: str = "open",
                     series_ticker: Optional[str] = None,
                     max_results: int = 200) -> list:
        """Markets matching ``status`` (default ``"open"``), optionally scoped
        to one ``series_ticker``, following the cursor up to ``max_results``."""
        out: list = []
        cursor: Optional[str] = None
        while len(out) < max_results:
            data = self._get("markets", {
                "status": status,
                "series_ticker": series_ticker,
                "limit": 1000,
                "cursor": cursor,
            })
            out.extend(data.get("markets", []))
            cursor = data.get("cursor")
            if not cursor:
                break
        return [normalize_market(m) for m in out[:max_results]]

    def list_events(self, *, status: str = "open",
                    with_nested_markets: bool = True,
                    max_results: int = 200) -> list:
        """Events matching ``status``, each with its (normalized) nested
        markets and a ``mutually_exclusive`` flag — the input to
        :func:`kalshi_bot_toolkit.arbitrage.field_scan`."""
        out: list = []
        cursor: Optional[str] = None
        while len(out) < max_results:
            data = self._get("events", {
                "status": status,
                "with_nested_markets": "true" if with_nested_markets else None,
                "limit": 200,
                "cursor": cursor,
            })
            for e in data.get("events", []):
                if with_nested_markets and e.get("markets"):
                    e["markets"] = [normalize_market(m) for m in e["markets"]]
                out.append(e)
            cursor = data.get("cursor")
            if not cursor:
                break
        return out[:max_results]

    def get_orderbook(self, ticker: str) -> dict:
        """Raw order book for a market (price levels in dollar strings)."""
        return self._get(f"markets/{ticker}/orderbook")
