# Task 012 — `MockMarketDataSource` Adapter

**Epic:** epic-003-simulation-generate-risk-paths
**Layer:** Infrastructure
**Sprint:** 03
**Depends on:** task-011
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## Context

Implements the `MarketDataSource` Protocol from `application/ports/market_data_source.py`. Reads the bundled CSV corpus via `CsvReturnMatrixLoader` and returns a `ReturnMatrix` for the requested universe. The first `HttpMarketDataSource` (v2) will be a parallel implementation of the same Protocol.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given the corpus is present and the universe is `(AAPL, MSFT, GOOG)`, When `MockMarketDataSource().load(universe)`, Then a `ReturnMatrix` is returned with `tickers = (AAPL, MSFT, GOOG)`, matching date ranges, `frequency = "daily"`, and `provider_version = <corpus version>`.
- [ ] **Scenario 2 (Sad Path):** Given the universe contains `UNKNOWN`, When `load`, Then `MarketDataLoadError` is raised with the offending ticker in `context`.
- [ ] **Edge Case (Mandatory):** If two tickers in the corpus have mismatched date ranges (which `task-010`'s loader should prevent but defense in depth), `load` MUST raise `ReturnMatrixCorpusError` rather than silently produce a misaligned matrix.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** Adds `tests/contract/test_market_data_source_contract.py` — a parameterized test that runs against any class implementing `MarketDataSource`. Today only `MockMarketDataSource` is tested; the v2 `HttpMarketDataSource` will be added to the same test in a future Epic.

## Out of Scope

- The v2 `HttpMarketDataSource` (deferred to v2 / Spike S-001).
- Caching the loaded `ReturnMatrix` between runs — re-reading the corpus is fast enough.
- Index/ETF composition logic (e.g., SPY's 500 holdings) — out of scope for v1.

## Deliverables

- `src/monte_carlo_risk/infrastructure/market_data/mock_market_data_source.py` — `class MockMarketDataSource(loader: ReturnMatrixLoader, corpus_dir: Path)` implementing `MarketDataSource`.
- `src/monte_carlo_risk/domain/simulation/return_matrix.py` — `class ReturnMatrix` value object matching the JSON Schema in `events.schema.json` §definitions.ReturnMatrix.
- `tests/unit/infrastructure/market_data/test_mock_market_data_source.py` — happy + sad + date-mismatch edge case.
- `tests/contract/test_market_data_source_contract.py` — first cross-implementation contract test.
