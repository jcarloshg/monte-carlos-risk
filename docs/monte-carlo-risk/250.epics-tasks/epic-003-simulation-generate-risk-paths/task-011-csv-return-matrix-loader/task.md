# Task 011 — CSV Return-Matrix Loader

**Epic:** epic-003-simulation-generate-risk-paths
**Layer:** Infrastructure
**Sprint:** 03
**Depends on:** task-010
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 300 LOC

## Context

Implements the `ReturnMatrixLoader` Protocol from `application/ports/return_matrix_loader.py`. Reads a single ticker's CSV and returns a `ReturnSeries`. Used by `MockMarketDataSource` (task-012) to assemble the full `ReturnMatrix`.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given `data/mock/AAPL.csv`, When I call `CsvReturnMatrixLoader().load(Ticker("AAPL"), Path("data/mock/AAPL.csv"))`, Then a `ReturnSeries` value object is returned with shape `(~1260,)` of `float` log returns and a date range.
- [ ] **Scenario 2 (Sad Path):** Given a non-existent path, When I call `load`, Then `ReturnMatrixLoadError` is raised with the path in `context`.
- [ ] **Edge Case (Mandatory):** If the CSV has rows with NaN or infinite `log_return` values (e.g., from a corrupted file), the loader MUST raise `ReturnMatrixLoadError` with the offending row number in `context`. Silent NaN propagation through `numpy.random` would corrupt the simulation.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** N/A — first contract test for this loader is in `task-012` (shared with `MockMarketDataSource`).

## Out of Scope

- The `MockMarketDataSource` that orchestrates multiple tickers (`task-012`).
- Caching the loaded CSVs in memory (acceptable to re-read; performance is fine for the corpus size).

## Deliverables

- `src/monte_carlo_risk/infrastructure/filesystem/csv_return_matrix_loader.py` — `class CsvReturnMatrixLoader` implementing `ReturnMatrixLoader`. Uses `pandas.read_csv` (whitelisted as a dev/infrastructure dependency only) or pure Python `csv` module — TBD by implementer.
- `src/monte_carlo_risk/domain/simulation/return_series.py` — `class ReturnSeries(dates: tuple[date, ...], values: ndarray)` value object.
- Typed exceptions in `src/monte_carlo_risk/domain/simulation/exceptions.py`: `ReturnMatrixLoadError`, `ReturnMatrixCorpusError` (the latter is also raised by `task-012`).
- `tests/unit/infrastructure/filesystem/test_csv_return_matrix_loader.py` — happy + sad + NaN edge case.
- New `pyproject.toml` dependency: `pandas>=2.0` (in `infrastructure` extras; not in domain).
