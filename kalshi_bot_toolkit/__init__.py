"""kalshi-bot-toolkit — open-source building blocks for Kalshi trading bots.

Edge detection, Kelly position sizing, and fee-aware math for the Kalshi
prediction market, plus a keyless reader for public market data. Built and
maintained by the team behind Bot for Kalshi (https://www.botforkalshi.com).
"""
from __future__ import annotations

from .fees import (
    Fee,
    calculate_fee,
    round_trip_fee_cents,
    min_profitable_target_offset,
)
from .kelly import kelly_stake
from .arbitrage import field_scan, scan_events
from .market_data import KalshiPublicClient, normalize_market

__version__ = "0.1.0"

__all__ = [
    "Fee",
    "calculate_fee",
    "round_trip_fee_cents",
    "min_profitable_target_offset",
    "kelly_stake",
    "field_scan",
    "scan_events",
    "KalshiPublicClient",
    "normalize_market",
    "__version__",
]
