# Task 015 — `RunSimulation` Orchestrator Extension (Portfolio + Sim)

**Epic:** epic-003-simulation-generate-risk-paths
**Layer:** Application
**Sprint:** 04
**Depends on:** task-009, task-012, task-014
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 300 LOC

## Context

Wires the first three contexts together via the `RunSimulation` orchestrator: Portfolio → MarketDataSource → Simulation. Emits `PortfolioDefined`, `MarketDataLoaded`, `SimulationStarted`, `SimulationCompleted`. RiskMetrics and Visualization are stubbed in this task (added in `task-020` and `task-024`). Traces to Story 3.1.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a valid portfolio + the mock corpus, When `RunSimulation.execute()`, Then four events are emitted in order: `PortfolioDefined`, `MarketDataLoaded`, `SimulationStarted`, `SimulationCompleted`. The return value is a partial `simulation_report` (path_set_summary populated; risk_report and artifacts absent).
- [ ] **Scenario 2 (Sad Path):** Given an invalid portfolio (weights don't sum), When `execute()`, Then NO `SimulationStarted` event is emitted; the use case raises `WeightsSumMustEqualOne` (the typed exception surfaces unchanged through the orchestrator).
- [ ] **Edge Case (Mandatory):** If the `event_sink.emit()` raises on any event, the orchestrator MUST NOT continue executing subsequent steps. Either it surfaces the exception (preferred — let the CLI convert to canonical error) or it transitions the `SimulationRun` to `Failed` and emits a `SimulationFailed` event. The behavior must be one of these two — never silent partial execution.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A — orchestrator is application-layer, not CLI.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** One `structlog` info line per emitted event. Concrete wiring expanded in `task-025`.
- [ ] **Contract Tests:** N/A — first cross-context contract test in `task-026`.

## Out of Scope

- The `RiskMetrics` step (Epic 004 / `task-020`).
- The `Visualization` step (Epic 005 / `task-024`).
- Idempotency assertions at the orchestrator level (`task-026`).

## Deliverables

- `src/monte_carlo_risk/application/use_cases/run_simulation.py` — `class RunSimulation(data_source: MarketDataSource, rng: DeterministicRNG, event_sink: EventSink)` with `execute(parameters, portfolio) -> SimulationReport`.
- `src/monte_carlo_risk/application/simulation_report.py` — `SimulationReport` value object with optional `path_set_summary`, `risk_report`, `artifacts` fields (only the first is populated by this task).
- Extension to `src/monte_carlo_risk/domain/portfolio/events.py` (already exists from `task-008`) — emit `PortfolioDefined`.
- New `src/monte_carlo_risk/domain/simulation/events.py` — `SimulationStarted`, `SimulationCompleted` event classes.
- `tests/unit/application/use_cases/test_run_simulation.py` — happy + sad + event-sink-raises edge case.
