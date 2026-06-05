from kalshi_bot_toolkit import normalize_market

# A market shaped like Kalshi's current public response (string dollars / fp).
RAW = {
    "ticker": "KXBTCD-26JUN0517-T55999.99",
    "title": "Bitcoin price on Jun 5, 2026?",
    "yes_ask_dollars": "1.0000",
    "yes_bid_dollars": "0.9500",
    "no_ask_dollars": "0.0500",
    "no_bid_dollars": "0.0000",
    "last_price_dollars": "0.9900",
    "volume_fp": "201.67",
    "open_interest_fp": "4388.00",
}


def test_parses_dollar_strings_to_cents():
    m = normalize_market(RAW)
    assert m["yes_ask"] == 100
    assert m["yes_bid"] == 95
    assert m["no_ask"] == 5
    assert m["last_price"] == 99


def test_parses_fixed_point_sizes():
    m = normalize_market(RAW)
    assert m["volume"] == 201.67
    assert m["open_interest"] == 4388.0


def test_yes_no_identity_holds():
    m = normalize_market(RAW)
    assert m["yes_bid"] + m["no_ask"] == 100
    assert m["yes_ask"] + m["no_bid"] == 100


def test_preserves_raw_keys_and_handles_missing():
    m = normalize_market({"ticker": "X"})
    assert m["ticker"] == "X"
    assert m["yes_ask"] is None
    assert m["last_price"] is None
    assert m["volume"] is None
