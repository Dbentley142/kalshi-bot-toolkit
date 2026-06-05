from kalshi_bot_toolkit import field_scan, scan_events


def _legs(asks, bids):
    return [{"yes_ask": a, "yes_bid": b} for a, b in zip(asks, bids)]


def test_buy_field_candidate_when_asks_sum_under_100():
    # 3 legs, Σask = 90c, fees ~6c -> buy_edge ~ +4c
    scan = field_scan(_legs([30, 30, 30], [28, 28, 28]),
                      mutually_exclusive=True)
    assert scan["candidate"] == "buy-field"
    assert scan["buy_edge"] > 0
    assert scan["sum_yes_ask"] == 90


def test_sell_field_candidate_when_bids_sum_over_100():
    scan = field_scan(_legs([42, 42, 42], [40, 40, 40]),
                      mutually_exclusive=True)
    assert scan["candidate"] == "sell-field"
    assert scan["sell_edge"] > 0


def test_non_mutually_exclusive_never_flags():
    # Same juicy numbers, but not mutually exclusive -> no candidate.
    scan = field_scan(_legs([30, 30, 30], [28, 28, 28]),
                      mutually_exclusive=False)
    assert scan["candidate"] is None
    assert scan["sum_yes_ask"] == 90  # sums still reported


def test_single_leg_is_not_a_field():
    assert field_scan(_legs([50], [48]), mutually_exclusive=True) is None


def test_scan_events_sorts_and_keeps_only_candidates():
    events = [
        {"event_ticker": "A", "title": "buyable", "mutually_exclusive": True,
         "markets": _legs([20, 20, 20], [18, 18, 18])},          # big buy edge
        {"event_ticker": "B", "title": "fair", "mutually_exclusive": True,
         "markets": _legs([34, 33, 33], [32, 32, 32])},          # ~no edge
        {"event_ticker": "C", "title": "not ME", "mutually_exclusive": False,
         "markets": _legs([20, 20, 20], [18, 18, 18])},          # excluded
    ]
    out = scan_events(events)
    assert [s["event_ticker"] for s in out] == ["A"]
    assert out[0]["candidate"] == "buy-field"
