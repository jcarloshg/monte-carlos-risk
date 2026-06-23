# Task 002 — Shared-Kernel Value Objects

**Epic:** epic-001-tracer-bullet-path-to-production
**Layer:** Domain
**Sprint:** 01
**Depends on:** task-001
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## Context

The Tracer Bullet needs at least one domain-layer file to prove the `domain/` package is correctly wired (so the linter in `task-004` has something to police). These are the four cross-context value objects used by every later Epic. Traces to Story 1.1.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given the value-object classes exist, When a unit test instantiates `Ticker("AAPL")`, `Weight(0.5)`, `Currency("USD")`, and `RunId(uuid4())`, Then each is constructed without error and exposes its value via `.value`.
- [ ] **Scenario 2 (Sad Path):** Given a string with lowercase characters, When I construct `Ticker("aapl")`, Then a typed `InvalidTickerError` is raised with the message "ticker must match `^[A-Z0-9.-]+$`".
- [ ] **Edge Case (Mandatory):** If a `Weight` is constructed with a value outside `[0, 1]`, the typed exception is raised at construction time (fail-fast, not at portfolio assembly time). NaN and infinity must also be rejected.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A — no CLI commands exposed yet.
- [ ] **Database Migrations:** N/A — no DB.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** N/A.

## Out of Scope

- The `Holding` and `Portfolio` value objects (Epic 002 / task-005).
- The `Return` value object (Epic 003 / task-014 — only needed once Simulation begins).
- Any use of `numpy` — shared kernel is stdlib + `uuid` only.

## Deliverables

- `src/monte_carlo_risk/domain/shared_kernel/__init__.py`
- `src/monte_carlo_risk/domain/shared_kernel/ticker.py` — `class Ticker(str)` with constructor validation, `regex=^[A-Z0-9.-]+$`, `InvalidTickerError`.
- `src/monte_carlo_risk/domain/shared_kernel/weight.py` — `class Weight(float)` with `__new__` enforcing `0 ≤ v ≤ 1`, rejecting NaN and `±inf`.
- `src/monte_carlo_risk/domain/shared_kernel/currency.py` — `class Currency(str)` validating against ISO-4217 (just three uppercase letters for v1).
- `src/monte_carlo_risk/domain/shared_kernel/run_id.py` — `class RunId(UUID)` wrapper.
- `tests/unit/domain/shared_kernel/test_ticker.py`, `test_weight.py`, `test_currency.py`, `test_run_id.py`.
