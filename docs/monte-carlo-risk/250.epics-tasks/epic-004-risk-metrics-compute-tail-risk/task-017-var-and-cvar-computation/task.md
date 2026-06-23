# Task 017 — VaR and CVaR Computation

**Epic:** epic-004-risk-metrics-compute-tail-risk
**Layer:** Domain
**Sprint:** 05
**Depends on:** task-014
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## Context

Pure-domain computation of Value-at-Risk and Expected Shortfall from a `PathSet`'s terminal-wealth distribution. The first "answer a quant question" task. Traces to Story 4.1.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a `PathSet` of 10,000 paths with terminal wealth uniformly distributed in `[0.5, 1.5]` and `confidence = 0.95`, `When` I compute `var(terminal_wealth, confidence)`, `Then` the result is approximately `0.5 + 0.05 * (1.5 - 0.5) = 0.525` (5th percentile of losses vs. starting value of 1.0 — but in our convention var is reported as a positive number representing loss, so the convention is reversed in the test).
- [ ] **Scenario 2 (Sad Path):** Given `confidence = 1.5`, `When` I compute `var`, `Then` `InvalidConfidenceError` is raised (must be in `(0, 1)`).
- [ ] **Edge Case (Mandatory):** Given a `PathSet` where ALL paths end at terminal wealth > 1.0 (no losses), `When` I compute `var` and `cvar`, `Then` both are **0** (no loss, no tail). The implementation must NOT raise on an all-winning distribution.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** N/A.

## Out of Scope

- Parametric VaR — v1 empirical only.
- The max-drawdown distribution (`task-018`).
- The `RiskReport` aggregate that bundles these (`task-019`).

## Deliverables

- `src/monte_carlo_risk/domain/risk_metrics/var.py` — pure functions: `var(losses: ndarray, confidence: float) -> float`, `cvar(losses: ndarray, confidence: float) -> float`. Convention: positive number = loss.
- `src/monte_carlo_risk/domain/risk_metrics/exceptions.py` — `InvalidConfidenceError`.
- `tests/unit/domain/risk_metrics/test_var.py` — happy + sad + all-winning edge cases.
- `tests/unit/domain/risk_metrics/test_cvar.py` — happy + sad + all-winning edge cases.
