"""List live markets in a Kalshi series, sorted by volume (no API key needed).

A series groups related markets. A few liquid ones:
    KXBTCD   Bitcoin price (daily)      KXETHD   Ethereum price (daily)
    KXHIGHNY High temperature, NYC      KXNBA    NBA game winners

    python examples/scan_markets.py <SERIES_TICKER>

Example:
    python examples/scan_markets.py KXBTCD
"""
import sys

from kalshi_bot_toolkit import KalshiPublicClient


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    series = sys.argv[1].upper()
    markets = KalshiPublicClient().list_markets(series_ticker=series,
                                                max_results=200)
    if not markets:
        print(f"No open markets in series {series!r}.")
        return 0

    print(f"\n{len(markets)} open market(s) in {series}:\n")
    print(f"  {'LAST':>4} {'BID':>4} {'ASK':>4} {'VOL':>9}  TICKER")
    for m in sorted(markets, key=lambda x: x.get("volume") or 0, reverse=True):
        print(f"  {_c(m.get('last_price')):>4} {_c(m.get('yes_bid')):>4} "
              f"{_c(m.get('yes_ask')):>4} {m.get('volume') or 0:>9,.0f}  "
              f"{m.get('ticker', '')}")
        print(f"        {m.get('title', '')}")
    return 0


def _c(cents) -> str:
    return f"{cents}c" if cents is not None else "-"


if __name__ == "__main__":
    raise SystemExit(main())
