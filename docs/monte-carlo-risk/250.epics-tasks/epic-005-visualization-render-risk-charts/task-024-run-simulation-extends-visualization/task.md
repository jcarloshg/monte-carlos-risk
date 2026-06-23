# Task 024 — `RunSimulation` Extends with Visualization

**Epic:** epic-005-visualization-render-risk-charts
**Layer:** Application
**Sprint:** 06
**Depends on:** task-020, task-022, task-023
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 300 LOC

## Context

The orchestrator (from `task-020`) gains a Visualization step. After `RiskMetricsCalculated`, it builds three `ChartArtifact`s, renders them via `MatplotlibRenderer`, writes them via `FilesystemOutputWriter`, and emits `ChartsRendered`. The full `simulation_report` is now complete. Traces to Story 5.1.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a successful simulation with risk metrics, `When` `RunSimulation.execute()`, Then six events are emitted in the canonical order (PortfolioDefined, MarketDataLoaded, SimulationStarted, SimulationCompleted, RiskMetricsCalculated, ChartsRendered). The returned `simulation_report` has `artifacts.{paths_png, drawdown_png, fan_chart_png, report_json}` populated with absolute paths.
- [ ] **Scenario 2 (Sad Path):** Given `--output-dir` is read-only, `When` `execute()`, `Then` the orchestrator's pre-flight writability check (`ensure_directory`) raises `OutputDirNotWritableError` BEFORE any simulation work begins (cheap check first, not after minutes of compute). The `SimulationRun` is never started.
- [ ] **Edge Case (Mandatory):** If the matplotlib renderer raises `VisualizationFailed` mid-chart (e.g., disk fills up after two PNGs but before the third), the orchestrator MUST emit a partial `ChartsRendered` event listing only the successfully-rendered artifacts (or MUST raise cleanly — the choice is recorded in this task's PR description). Silent partial completion is forbidden.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A — orchestrator is application-layer.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** One `structlog` info line for `ChartsRendered`. Full wiring in `task-025`.
- [ ] **Contract Tests:** N/A — first cross-context contract test in `task-026`.

## Out of Scope

- Real observability/dashboards (Epic 006 / `task-025`).
- Determinism tests (`task-026`).
- Benchmark gate (`task-027`).

## Deliverables

- Extension to `src/monte_carlo_risk/application/use_cases/run_simulation.py` — add Visualization step after RiskMetrics step; pre-flight writability check at the very start of `execute()`.
- Extension to `src/monte_carlo_risk/application/simulation_report.py` — `artifacts` field now required (was optional); paths populated.
- `tests/unit/application/use_cases/test_run_simulation_viz.py` — happy + read-only-output-dir sad + partial-render edge case.
- `tests/integration/application/test_run_simulation_full_e2e.py` — first end-to-end test that runs the entire pipeline (Portfolio → MDS → Sim → Risk → Viz) and asserts all 6 events + artifacts.
