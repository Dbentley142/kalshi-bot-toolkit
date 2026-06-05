# Changelog

## 0.1.0

Initial release.

- `kelly_stake()` — full and fractional Kelly sizing for Kalshi YES contracts,
  with edge %, expected value, and an over-betting warning.
- `calculate_fee()`, `round_trip_fee_cents()`, `min_profitable_target_offset()`
  — Kalshi's per-contract fee model, with maker rebate.
- `field_scan()` / `scan_events()` — fee-aware structural field-sum mispricing
  scanner for mutually-exclusive multi-outcome events, with an exhaustiveness
  caveat (mutually-exclusive ≠ collectively exhaustive).
- `KalshiPublicClient` — keyless reader for public market data
  (`get_market`, `list_markets`, `list_events`, `get_orderbook`), parsing
  Kalshi's `*_dollars` / `*_fp` string schema into clean cents via
  `normalize_market()`.
- Examples: `find_edge`, `scan_markets`, `fee_aware_target`, `scan_arbitrage`.
- Zero runtime dependencies (standard library only).
