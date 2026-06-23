# Task 018 — Max-Drawdown Distribution

**Epic:** epic-004-risk-metrics-compute-tail-risk
**Layer:** Domain
**Sprint:** 05
**Depends on:** task-014
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## Context

Computes the per-path max drawdown from a `PathSet` and summarizes its distribution. The third headline risk number (alongside VaR/CVaR). Traces to Story 4.2.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a `PathSet` of paths starting at wealth 1.0, `When` I compute the max-drawdown distribution, `Then` `mean`, `std`, `p05`, `p50`, `p95` are present and `p05 ≤ p50 ≤ p95` (monotonic percentiles).
- [ ] **Scenario 2 (Sad Path):** Given a `PathSet` with empty `terminal_wealth`, `When` I compute the distribution, `Then `EmptyPathSetError` is raised.
- [ ] **Edge Case (Mandatory):** Given a path that monotonically increases (never has a drawdown), `When` I compute its max drawdown, `Then` the max drawdown is `0` (no loss from peak). The function must NOT return a negative number.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** N/A.

## Out of Scope

- The terminal-wealth distribution (a simpler statistic; computed inline in `task-019`).
- Conditional drawdown analysis (e.g., "max drawdown in the last 63 days") — v2.

## Deliverables

- `src/monte_carlo_risk/domain/risk_metrics/drawdown.py` — pure functions: `max_drawdown_per_path(path: ndarray) -> float` (returns a negative number or 0), `max_drawdown_distribution(max_drawdowns: ndarray) -> DistributionSummary`.
- `src/monte_carlo_risk/domain/risk_metrics/distribution_summary.py` — `@dataclass(frozen=True) class DistributionSummary(mean, std, p05, p50, p95)`.
- `src/monte_carlo_risk/domain/risk_metrics/exceptions.py` (extend) — `EmptyPathSetError`.
- `tests/unit/domain/risk_metrics/test_drawdown.py` — happy + sad + monotonic-path edge case.
- `tests/unit/domain/risk_metrics/test_distribution_summary.py` — monotonic-percentile invariant + std ≥ 0 invariant.
