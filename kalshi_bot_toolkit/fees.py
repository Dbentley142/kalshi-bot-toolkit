"""Fee calculation for Kalshi trades — pure and dependency-free.

Kalshi charges per-contract fees that depend on the trade price and whether
you are the maker (a limit order resting on the book) or the taker (an
immediate fill).

Formula (per Kalshi's published schedule)::

    per_contract_fee = ceil(0.07 * count * price * (1 - price))

where ``price`` is in dollars (``price_cents / 100``). Maker orders that rest
on the book and get filled receive a rebate; we model this as a ~50%
reduction. The fee is highest at 50c (where ``p*(1-p)`` peaks) and approaches
zero near 1c or 99c.
"""
from __future__ import annotations

import math


class Fee(int):
    """Result of :func:`calculate_fee`. Behaves as an ``int`` (net fee in
    cents) so ``a + b`` and ``f"{fee}c"`` keep working, while exposing the
    structured breakdown for callers that need it.

    Attributes:
        trading_fee_cents:      raw per-trade fee charged by Kalshi
        volume_incentive_cents: rebate from the maker / volume program
        net_fee_cents:          trading_fee_cents - volume_incentive_cents
        is_maker:               True if treated as a maker order
    """

    trading_fee_cents: int
    volume_incentive_cents: int
    net_fee_cents: int
    is_maker: bool

    def __new__(cls, net_fee_cents: int, *, trading_fee_cents: int,
                volume_incentive_cents: int, is_maker: bool) -> "Fee":
        instance = super().__new__(cls, int(net_fee_cents))
        instance.trading_fee_cents = int(trading_fee_cents)
        instance.volume_incentive_cents = int(volume_incentive_cents)
        instance.net_fee_cents = int(net_fee_cents)
        instance.is_maker = bool(is_maker)
        return instance

    def __repr__(self) -> str:
        return (f"Fee(net={self.net_fee_cents}c, "
                f"raw={self.trading_fee_cents}c, "
                f"rebate={self.volume_incentive_cents}c, "
                f"maker={self.is_maker})")

    def __str__(self) -> str:
        return str(int(self))

    def __format__(self, format_spec: str) -> str:
        return format(int(self), format_spec)


def calculate_fee(*, price_cents: int, count: int,
                  is_maker: bool = False) -> Fee:
    """Return the fee for a Kalshi trade.

    The integer value of the returned :class:`Fee` is the **net** fee in
    cents, so ``calculate_fee(...) + other_int`` keeps working.

    Args:
        price_cents: trade price in cents (1-99). 0 or 100 -> no fee.
        count:       number of contracts.
        is_maker:    True if the order rests on the book and gets the rebate.
    """
    if count <= 0 or price_cents <= 0 or price_cents >= 100:
        return Fee(0, trading_fee_cents=0, volume_incentive_cents=0,
                   is_maker=is_maker)

    p = price_cents / 100.0
    raw_dollars = 0.07 * count * p * (1.0 - p)
    trading_fee_cents = math.ceil(raw_dollars * 100)

    if is_maker:
        net_fee_cents = max(0, trading_fee_cents // 2)
        volume_incentive_cents = trading_fee_cents - net_fee_cents
    else:
        net_fee_cents = trading_fee_cents
        volume_incentive_cents = 0

    return Fee(
        net_fee_cents,
        trading_fee_cents=trading_fee_cents,
        volume_incentive_cents=volume_incentive_cents,
        is_maker=is_maker,
    )


def round_trip_fee_cents(*, entry_price_cents: int, exit_price_cents: int,
                         count: int,
                         entry_is_maker: bool = False,
                         exit_is_maker: bool = True) -> int:
    """Total net fee in cents for a buy-then-sell round trip.

    Defaults assume the buy crosses the spread (taker) for a fast fill while
    the sell rests on the book (maker rebate). Override to model other styles.
    """
    bf = calculate_fee(price_cents=entry_price_cents, count=count,
                       is_maker=entry_is_maker)
    sf = calculate_fee(price_cents=exit_price_cents, count=count,
                       is_maker=exit_is_maker)
    return int(bf) + int(sf)


def min_profitable_target_offset(*, entry_price_cents: int, count: int,
                                 min_edge_cents: int = 1,
                                 max_offset_cents: int = 50) -> int:
    """Smallest sell-target offset (cents above entry) whose net P&L clears
    fees by at least ``min_edge_cents``.

    The exit fee depends on the chosen target, so this iterates upward from
    1c rather than solving in closed form. Returns ``max_offset_cents`` if no
    profitable target exists in range (treat that as "do not enter").
    """
    if count <= 0 or entry_price_cents <= 0 or entry_price_cents >= 99:
        return max_offset_cents
    for offset in range(1, max_offset_cents + 1):
        exit_price = entry_price_cents + offset
        if exit_price >= 100:
            return max_offset_cents
        fees = round_trip_fee_cents(
            entry_price_cents=entry_price_cents,
            exit_price_cents=exit_price,
            count=count,
        )
        gross = offset * count
        if gross - fees >= min_edge_cents:
            return offset
    return max_offset_cents
