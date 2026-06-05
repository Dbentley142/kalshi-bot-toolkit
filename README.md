# Kalshi Bot Toolkit

**Open-source Python building blocks for Kalshi trading bots** — edge detection, Kelly position sizing, and fee-aware math, plus a keyless reader for live Kalshi market data. Zero dependencies, MIT-licensed.

![python](https://img.shields.io/badge/python-3.9%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![tests](https://img.shields.io/badge/tests-18%20passing-brightgreen)

> Built and maintained by the team behind **[Bot for Kalshi](https://www.botforkalshi.com)** — a no-code platform for automated Kalshi trading. This toolkit is the open-source math we use, packaged for anyone building their own bot.

If you are building a Kalshi trading bot in Python, three problems show up immediately: *am I actually getting an edge at this price?*, *how much should I bet?*, and *do the fees eat my profit?* This toolkit answers all three with small, tested, dependency-free functions.

## Install

```bash
pip install kalshi-bot-toolkit
# or, from source:
git clone https://github.com/Dbentley142/kalshi-bot-toolkit
cd kalshi-bot-toolkit && pip install -e .
```

No API key needed for market data — Kalshi's public price feed is open. (Placing orders needs your own signed Kalshi key; that is out of scope here on purpose.)

## Quickstart: find your edge

You bring a probability estimate; the toolkit tells you the edge, the expected value, and a sane bet size.

```python
from kalshi_bot_toolkit import KalshiPublicClient, kelly_stake

client = KalshiPublicClient()

# Prices are parsed to cents for you (Kalshi's raw API returns dollar strings).
m = client.get_market("KXBTCD-26JUN0517-T55999.99")
print(m["yes_ask"], m["last_price"], m["volume"])   # e.g. 62 61 201.67

r = kelly_stake(bankroll=1000, p_pct=70, price_c=m["yes_ask"])
print(r["edge_pct"])    # +12.9   -> your 70% vs the market's 62c
print(r["ev_cents"])    # +8.0    -> expected value per contract
print(r["stake_half"])  # half-Kelly stake in dollars
print(r["note"])        # plain-language risk warning
```

Run the examples directly (tickers rotate daily — scan to find a live one):

```bash
python examples/scan_markets.py KXBTCD                 # list a market series
python examples/find_edge.py <TICKER> 70 1000          # edge + Kelly stake
python examples/fee_aware_target.py 50 10              # min profitable exit
python examples/scan_arbitrage.py 300                  # structural field-sum scan
```

## What's inside

| Function | What it does |
|---|---|
| `kelly_stake()` | Full and fractional (½, ¼) Kelly sizing for a Kalshi YES, with edge %, expected value, and an over-betting warning. |
| `calculate_fee()` | Kalshi's per-contract fee (`ceil(0.07 · n · p · (1−p))`), maker rebate modeled. |
| `round_trip_fee_cents()` / `min_profitable_target_offset()` | Fee on a buy-then-sell, and the smallest sell target that actually clears fees. |
| `field_scan()` / `scan_events()` | Fee-aware **structural mispricing** scan of mutually-exclusive events — with an honest exhaustiveness caveat (most "fields under 100¢" are *not* free money). |
| `KalshiPublicClient` | Keyless reader: `get_market`, `list_markets(series_ticker=…)`, `list_events`, `get_orderbook`. |
| `normalize_market()` | Parse Kalshi's raw `*_dollars` / `*_fp` strings into clean cent/number keys. |

Everything is pure Python standard library — no `requests`, no SDK, no account required to compute. Markets are grouped under a **series** (`KXBTCD` = Bitcoin daily, `KXETHD` = Ethereum, `KXHIGHNY` = NYC high temp…); filtering by `series_ticker` is the reliable way to list a group.

Edge is honest: **you** supply the probability. The toolkit never pretends to have a magic model; it just does the math correctly and warns you when a price has no edge.

## How this relates to the hosted product

This toolkit gives you the primitives. If you would rather **not** wire up Python, a server, and the order API yourself:

| | Kalshi Bot Toolkit (this repo) | [Bot for Kalshi](https://www.botforkalshi.com) |
|---|---|---|
| Setup | Write Python, run it yourself | No code — visual builder |
| Edge / Kelly math | ✅ (these functions) | ✅ built in |
| Live order execution | DIY (your key) | ✅ sub-50ms, managed |
| Monitoring, stop conditions, kill switch | DIY | ✅ built in |
| Cost | Free | $99/mo flat |

Same math, two ways to use it. Star this repo if it saved you time.

## Disclaimer

Not affiliated with or endorsed by Kalshi. Trading on prediction markets involves real financial risk; this software is provided for educational and research purposes with no warranty. Past performance does not predict future results. You are responsible for your own trades and for complying with Kalshi's terms and applicable regulations.

## License

MIT — see [LICENSE](LICENSE). Contributions welcome.
