"""Find your edge on a single Kalshi market.

You bring a probability estimate; this prints the edge versus the live
price, the expected value per contract, and a fractional-Kelly stake.

    python examples/find_edge.py <TICKER> <YOUR_PROBABILITY_%> [BANKROLL_$]

Tickers rotate daily — grab a live one with:
    python examples/scan_markets.py KXBTCD
"""
import sys

from kalshi_bot_toolkit import KalshiPublicClient, kelly_stake


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1

    ticker = sys.argv[1]
    p_pct = float(sys.argv[2])
    bankroll = float(sys.argv[3]) if len(sys.argv) > 3 else 1000.0

    m = KalshiPublicClient().get_market(ticker)

    # Cost to buy YES now is the yes_ask; if there's no real ask (illiquid,
    # shows 100c), fall back to the last traded price as a reference.
    yes_ask = m.get("yes_ask")
    if yes_ask and 1 <= yes_ask <= 99:
        price, label = yes_ask, "yes_ask"
    else:
        price, label = m.get("last_price"), "last_price"

    if not price or not (1 <= price <= 99):
        print(f"No tradeable YES price for {ticker} "
              f"(yes_ask={m.get('yes_ask')}, last={m.get('last_price')}).")
        return 1

    r = kelly_stake(bankroll=bankroll, p_pct=p_pct, price_c=price)
    if not r["ok"]:
        print(f"Error: {r['error']}")
        return 1

    print(f"\n{m.get('title', ticker)}")
    print(f"  Ticker            {ticker}")
    print(f"  Price ({label:<10}) {price}c  (= {price}% implied)")
    print(f"  Your probability  {p_pct:.0f}%")
    print(f"  Edge              {r['edge_pct']:+.1f}%   "
          f"(EV {r['ev_cents']:+.1f}c / contract)")
    if r["no_bet"]:
        print(f"\n  {r['note']}")
        return 0
    print(f"  Half-Kelly stake  ${r['stake_half']:.2f}  "
          f"(~{int(r['stake_half'] * 100 // price)} contracts)")
    print(f"\n  {r['note']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
