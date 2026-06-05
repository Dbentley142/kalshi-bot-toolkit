from kalshi_bot_toolkit import calculate_fee, round_trip_fee_cents


def test_fee_peaks_at_midprice():
    mid = calculate_fee(price_cents=50, count=100)
    edge = calculate_fee(price_cents=10, count=100)
    assert int(mid) > int(edge)  # p*(1-p) is largest at 50c


def test_no_fee_at_boundaries():
    assert int(calculate_fee(price_cents=0, count=10)) == 0
    assert int(calculate_fee(price_cents=100, count=10)) == 0
    assert int(calculate_fee(price_cents=50, count=0)) == 0


def test_maker_rebate_reduces_fee():
    taker = calculate_fee(price_cents=50, count=100, is_maker=False)
    maker = calculate_fee(price_cents=50, count=100, is_maker=True)
    assert int(maker) <= int(taker)
    assert maker.volume_incentive_cents > 0


def test_fee_behaves_as_int():
    fee = calculate_fee(price_cents=50, count=10)
    assert fee + 5 == int(fee) + 5
    assert f"{fee}c".endswith("c")


def test_round_trip_sums_both_legs():
    rt = round_trip_fee_cents(entry_price_cents=50, exit_price_cents=55,
                              count=10)
    assert rt > 0
