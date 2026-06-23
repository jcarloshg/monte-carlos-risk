# Task 019 — `RiskReport` Aggregate

**Epic:** epic-004-risk-metrics-compute-tail-risk
**Layer:** Domain
**Sprint:** 05
**Depends on:** task-017, task-018
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 300 LOC

## Context

The RiskMetrics aggregate root. Bundles VaR, CVaR, drawdown distribution, and terminal-wealth distribution into a single immutable value object. Computed by a single factory `RiskReport.from_path_set(path_set, confidence)`. Traces to Stories 4.1, 4.2.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a valid `PathSet` and `confidence = 0.95`, `When` `RiskReport.from_path_set(path_set, confidence)`, Then a `RiskReport` is returned with all five required sub-objects: `var`, `cvar`, `max_drawdown_distribution`, `terminal_wealth_distribution`, plus the echoed `confidence`.
- [ ] **Scenario 2 (Sad Path):** Given an empty `PathSet`, `When` `from_path_set`, Then `EmptyPathSetError` is raised (same exception as `task-018`).
- [ ] **Edge Case (Mandatory):** The `RiskReport` is `@dataclass(frozen=True)`. Any attempt to mutate an attribute (e.g., `report.var = 0.0`) MUST raise `FrozenInstanceError` from `dataclasses`. A unit test asserts this — frozen reports are critical for downstream event immutability.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** N/A.

## Out of Scope

- Wiring `RiskReport` into the orchestrator (`task-020`).
- Rendering risk metrics as charts (Epic 005).
- The `RiskMetricsCalculated` event class itself (lives in `domain/risk_metrics/events.py`, emitted by `task-020`).

## Deliverables

- `src/monte_carlo_risk/domain/risk_metrics/risk_report.py` — `@dataclass(frozen=True, slots=True) class RiskReport(confidence, var, cvar, max_drawdown_distribution, terminal_wealth_distribution)` with `@classmethod from_path_set(path_set, confidence) -> RiskReport`.
- `src/monte_carlo_risk/domain/risk_metrics/events.py` — `RiskMetricsCalculated` event class.
- `tests/unit/domain/risk_metrics/test_risk_report.py` — happy + sad + frozen-immutability edge case.
