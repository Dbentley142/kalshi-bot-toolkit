# Contributing

Thanks for your interest! This toolkit stays small, correct, and **dependency-free**.

## Ground rules

- **Standard library only.** No `requests`, no SDKs, no heavy deps. If you need
  HTTP, use `urllib` like `market_data.py` does.
- **Pure functions where possible.** The math modules (`fees`, `kelly`,
  `arbitrage`) take inputs and return values — no network, no globals.
- **Be honest.** This toolkit never claims a magic edge or "free money." If a
  result has a caveat (exhaustiveness, liquidity, a wrong probability estimate),
  surface it in the output, like the scanners already do.

## Dev setup

```bash
pip install -e .
pip install pytest
pytest -q
```

All tests are offline (no network), so they run anywhere and in CI.

## Pull requests

- Add or update a test for any behavior change.
- Keep the public API in `__init__.py` tidy and documented.
- Run `pytest -q` before opening the PR.
