"""Find the smallest profitable sell target after Kalshi fees.

A 1c move does not always cover the round-trip fee. This prints the
smallest exit offset whose net P&L clears fees.

    python examples/fee_aware_target.py <ENTRY_PRICE_c> <CONTRACTS>

Example:
    python examples/fee_aware_target.py 50 10
"""
import sys

from kalshi_bot_toolkit import min_profitable_target_offset, round_trip_fee_cents


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1

    entry = int(sys.argv[1])
    count = int(sys.argv[2])

    offset = min_profitable_target_offset(entry_price_cents=entry, count=count)
    fee = round_trip_fee_cents(entry_price_cents=entry,
                               exit_price_cents=entry + offset, count=count)
    gross = offset * count
    print(f"\n  Entry            {entry}c x {count} contracts")
    print(f"  Round-trip fee   {fee}c")
    print(f"  Min sell target  {entry + offset}c  (+{offset}c)")
    print(f"  Net at target    {gross - fee:+d}c "
          f"(gross {gross}c - fee {fee}c)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
