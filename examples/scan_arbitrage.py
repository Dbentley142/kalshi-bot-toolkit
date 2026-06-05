"""Scan open Kalshi events for structural field-sum mispricings (no API key).

For a mutually-exclusive event where exactly one outcome wins, buying every
YES for less than 100c (or selling every YES for more) is a structural edge.
Most flags are NOT free money — see the caveat the scanner prints.

    python examples/scan_arbitrage.py [MAX_EVENTS]

Example:
    python examples/scan_arbitrage.py 300
"""
import sys

from kalshi_bot_toolkit import KalshiPublicClient, scan_events


def main() -> int:
    max_events = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    events = KalshiPublicClient().list_events(max_results=max_events)
    flagged = scan_events(events)

    me_multi = [e for e in events
                if e.get("mutually_exclusive") and len(e.get("markets") or []) >= 2]
    print(f"\nScanned {len(events)} events "
          f"({len(me_multi)} mutually-exclusive fields). "
          f"{len(flagged)} candidate(s):\n")

    if not flagged:
        print("  No field-sum candidates right now.")
    for s in flagged[:15]:
        edge = s["buy_edge"] if s["candidate"] == "buy-field" else s["sell_edge"]
        print(f"  [{s['candidate']:>10}] edge {edge:+.1f}c  "
              f"(Σask={s['sum_yes_ask']} Σbid={s['sum_yes_bid']}, "
              f"{s['legs']} legs)  {s['event_ticker']}")
        print(f"               {s['title']}")

    print(f"\n  ⚠ {flagged[0]['caveat'] if flagged else scan_caveat()}")
    return 0


def scan_caveat() -> str:
    return ("Mutually-exclusive != exhaustive. A low Σ(YES_ask) usually means "
            "an unlisted outcome could win, not free money. Verify before trading.")


if __name__ == "__main__":
    raise SystemExit(main())
