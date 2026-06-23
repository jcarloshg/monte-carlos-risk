# ADR-003 — Mock-First `MarketDataSource` with Python `Protocol` Port

- **Status:** Accepted
- **Date:** 2026-06-23
- **Deciders:** jcarloshg
- **Source:** `00.defining.md` §1 Dependencies, §2 Contracts; `01.planning.md` §1 Bounded Contexts.

## Context

The README explicitly states the long-term intent: "in the future I want to connect third party API to get more information" (`README.md` line 11). Today the project uses mock data only. The risk is that the v1 code embeds the mock data source so deeply that swapping in a real API later requires a refactor of the simulation or risk code.

The defining phase narrowed the future API to **market data** — candidates are Yahoo Finance, Alpha Vantage, or Polygon.io — with vendor selection deferred to a timeboxed Spike (S-001). Until that spike completes, the v1 code must be ready to absorb any of the three.

## Options

1. **No abstraction.** v1 calls a `load_csv(path)` function directly. Future API integration rewrites the simulation use case.
2. **Abstract base class (`ABC`)** with `load() -> ReturnMatrix`. Forces inheritance; not duck-typed; awkward for testing.
3. **Python `Protocol` (PEP 544)** with structural typing. The simulation use case depends on `MarketDataSource` (a Protocol); any class with the right methods satisfies it. Two reference implementations: `MockMarketDataSource` (v1) and `HttpMarketDataSource` (v2).

## Decision

**Option 3: Python `Protocol` as the port.**

- `application/ports/market_data_source.py` defines `class MarketDataSource(Protocol): def load(self, universe: tuple[Ticker, ...]) -> ReturnMatrix: ...`.
- `infrastructure/mock_market_data_source.py` implements it by reading bundled CSV files from `data/mock/`.
- `infrastructure/http_market_data_source.py` is **stubbed in v1** with a `NotImplementedError` raise + a `@pytest.mark.xfail(reason="v2 — gated by Spike S-001")` test. This keeps the seam visible in v1 without delivering v2.
- The application orchestrator depends only on the `Protocol`, not on either implementation. Selecting which adapter is used at runtime is a CLI flag (`--provider mock|http`, default `mock`).

## Consequences

**Positive.**
- v2 work is a drop-in: write `HttpMarketDataSource.load()`, delete the xfail, ship. Zero domain changes.
- The contract test suite for `MarketDataSource` (`tests/contract/test_market_data_source_contract.py`) is the single source of truth for what "correct" means — every new vendor adapter must pass it.
- The seam is visible in the v1 code, so future contributors don't accidentally bypass it.

**Negative.**
- One extra layer of indirection. Mitigated by the Protocol being a 5-line file and the benefit being large.
- Protocol typing is checked by `mypy --strict`; if `mypy` is not in CI, drift is possible. **Mitigated by adding `mypy --strict` to the CI lint job.**

**Supersedes.** None.
