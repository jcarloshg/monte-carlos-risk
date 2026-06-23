# Task 020 — `RunSimulation` Extends with RiskMetrics

**Epic:** epic-004-risk-metrics-compute-tail-risk
**Layer:** Application
**Sprint:** 05
**Depends on:** task-016, task-019
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 200 LOC

## Context

The orchestrator (from `task-015`) gains a RiskMetrics step. After `SimulationCompleted`, the orchestrator computes `RiskReport.from_path_set` and emits `RiskMetricsCalculated`. The `simulation_report.json` now has `risk_report` populated. Traces to Story 4.3.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a successful simulation, `When` `RunSimulation.execute()`, Then five events are emitted in order: `PortfolioDefined`, `MarketDataLoaded`, `SimulationStarted`, `SimulationCompleted`, `RiskMetricsCalculated`. The returned `simulation_report` has both `path_set_summary` and `risk_report` populated.
- [ ] **Scenario 2 (Sad Path):** Given `RiskReport.from_path_set` raises `EmptyPathSetError` (defensive — shouldn't happen if Simulation succeeded, but defense in depth), `When` `execute()`, Then `SimulationRun` transitions to `Failed` and no `RiskMetricsCalculated` event is emitted. The typed exception surfaces to the CLI for canonical error envelope.
- [ ] **Edge Case (Mandatory):** If `confidence` is outside `(0, 1)`, the orchestrator MUST validate it BEFORE the simulation starts (cheap check first). This prevents minutes of wasted simulation on an invalid confidence level.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A — orchestrator is application-layer.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** One `structlog` info line for `RiskMetricsCalculated`. Full wiring in `task-025`.
- [ ] **Contract Tests:** N/A.

## Out of Scope

- The Visualization step (Epic 005 / `task-024`).
- The `RiskMetricsCalculated` event payload schema (already frozen).

## Deliverables

- Extension to `src/monte_carlo_risk/application/use_cases/run_simulation.py` — add RiskMetrics step after Simulation step.
- Extension to `src/monte_carlo_risk/application/simulation_report.py` — `risk_report` field now required (was optional).
- New exception `RiskMetricsFailed` (added to `domain/risk_metrics/exceptions.py`) wrapping `RiskReport.from_path_set` errors at the orchestrator boundary.
- `tests/unit/application/use_cases/test_run_simulation_risk.py` — happy + sad + invalid-confidence edge case.
