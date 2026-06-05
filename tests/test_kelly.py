from kalshi_bot_toolkit import kelly_stake


def test_positive_edge_when_prob_above_price():
    r = kelly_stake(bankroll=1000, p_pct=60, price_c=50)
    assert r["ok"]
    assert r["edge_pct"] > 0
    assert r["ev_cents"] == 10  # 60c fair value - 50c price
    assert not r["no_bet"]
    assert r["stake_full"] > 0


def test_no_bet_when_price_too_high():
    r = kelly_stake(bankroll=1000, p_pct=40, price_c=50)
    assert r["ok"]
    assert r["no_bet"]
    assert r["stake_full"] == 0
    assert "DO NOT BET" in r["note"]


def test_half_kelly_is_half_of_full():
    r = kelly_stake(bankroll=1000, p_pct=70, price_c=50)
    assert r["stake_half"] == round(r["stake_full"] * 0.5, 2)
    assert r["stake_quarter"] == round(r["stake_full"] * 0.25, 2)


def test_invalid_input_returns_error():
    assert not kelly_stake(bankroll=0, p_pct=60, price_c=50)["ok"]
    assert not kelly_stake(bankroll=1000, p_pct=120, price_c=50)["ok"]
    assert not kelly_stake(bankroll=1000, p_pct=60, price_c=0)["ok"]
