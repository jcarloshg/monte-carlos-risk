# Task 010 — Bundled Mock CSV Corpus

**Epic:** epic-003-simulation-generate-risk-paths
**Layer:** Data
**Sprint:** 03
**Depends on:** task-004
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 300 LOC (mostly generated CSV data)

## Context

The v1 source of historical return distributions per `ADR-003`. One CSV per ticker in `data/mock/`. Each CSV has columns `date,log_return`. ~5 years of daily data (~1,260 trading days) per ticker across ~30 tickers. The data is **synthetic but realistic**: sampled from a calibrated per-ticker distribution (mean, volatility drawn from a plausible equity universe). Versioned via git.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given `data/mock/AAPL.csv` exists with columns `date,log_return` and at least 1,260 rows, When a downstream loader reads it, Then the file parses without error and the rows are date-sorted ascending.
- [ ] **Scenario 2 (Sad Path):** Given a CSV missing the `log_return` column, When the loader attempts to parse it, Then `ReturnMatrixCorpusError` is raised with the missing column name in `context`.
- [ ] **Edge Case (Mandatory):** If a future contributor adds a ticker to `data/mock/` with a different date range than the others, the loader MUST detect the mismatch and raise `ReturnMatrixCorpusError` listing the offending dates. This protects reproducibility (NFR-4 — all tickers must share the same date range).

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A — but the mock corpus IS the data layer per `diagrams/db-erd.md` §What lives where instead.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** A `mock_data_version` is computed at load time from `git describe --tags --always` of the repo at the data dir. Recorded in the `ReturnMatrix.provider_version` field per `events.schema.json`.
- [ ] **Contract Tests:** N/A — first contract test for the corpus is in `task-012` (when MDS uses it).

## Out of Scope

- Real market-data adapter (`HttpMarketDataSource`) — v2.
- Per-ticker fundamental data (P/E, market cap) — N/A for v1.
- Multiple data frequencies (intraday, monthly) — daily only in v1.

## Deliverables

- `data/mock/AAPL.csv`, `data/mock/MSFT.csv`, …, `data/mock/GOOG.csv` — 30 ticker CSVs with `date,log_return`. Tickers chosen from a stable educational set (mega-cap tech + SPY + a bond ETF for diversification examples).
- `data/mock/MOCK_DATA_VERSION.txt` — semantic version of the corpus (`0.1.0-stub` for v1).
- `scripts/generate_mock_corpus.py` — committed script that regenerates the corpus from a fixed seed (so future maintainers can reproduce). Marked clearly as "not part of runtime."
- `tests/unit/data/test_mock_corpus.py` — asserts shape, date alignment, and version presence.
