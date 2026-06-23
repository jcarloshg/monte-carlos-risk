# Task 014 — `SimulationRun` Aggregate + State Machine

**Epic:** epic-003-simulation-generate-risk-paths
**Layer:** Domain
**Sprint:** 03
**Depends on:** task-013
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 350 LOC

## Context

The Simulation context's aggregate root. Encodes the state machine from `100.planning/diagrams/state-machine-simulation-run.md` (7 legal transitions, 7 forbidden) and the path-generation math. Consumes a `DeterministicRNG` via constructor injection. Returns a `PathSet` on `complete()`.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a `SimulationRun(parameters=N(p=10000, h=252, seed=1729), portfolio, return_matrix)`, When I call `.start()` then `.complete()`, Then a `PathSet` is returned with `shape = (10000, 253)`, `terminal_wealth.shape = (10000,)`, and `max_drawdown_per_path.shape = (10000,)`. The state machine transitions through `Pending → Running → Completed` exactly once.
- [ ] **Scenario 2 (Sad Path):** Given `n_paths = 0`, When I construct `SimulationRun`, Then `InvalidSimulationParameterError` is raised at construction (fail-fast). Same for `horizon = 0` or `seed < 0`.
- [ ] **Scenario 3 (Forbidden Transition):** Given a `SimulationRun` in `Running`, When I call `.start()` again, Then `InvalidSimulationTransition` is raised. Per the state machine, `Running → Pending` is explicitly forbidden.
- [ ] **Edge Case (Mandatory):** If `rng.normal(...)` raises mid-simulation (e.g., memory exhaustion under extreme `n_paths=1_000_000`), the aggregate MUST transition to `Failed` with `error_reason` set, and `complete()` MUST NOT return a partial `PathSet`. The state machine must not allow recovery from `Failed` without constructing a new aggregate.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** N/A.

## Out of Scope

- The orchestrator that calls this aggregate (`task-015`).
- The CLI command (`task-016`).
- Variance reduction (`task-014` uses plain Monte Carlo).

## Deliverables

- `src/monte_carlo_risk/domain/simulation/parameters.py` — `@dataclass(frozen=True) class SimulationParameters(n_paths, horizon, seed, provider)` matching `events.schema.json` §definitions.SimulationParameters.
- `src/monte_carlo_risk/domain/simulation/path.py` — `class Path` value object (numpy array wrapper).
- `src/monte_carlo_risk/domain/simulation/path_set.py` — `@dataclass(frozen=True) class PathSet` matching `events.schema.json` §definitions.PathSet.
- `src/monte_carlo_risk/domain/simulation/simulation_run.py` — `class SimulationRun` with state machine: `start()`, `complete(path_set)`, `fail(reason)`, private `_state` field, `InvalidSimulationTransition` on illegal moves.
- `src/monte_carlo_risk/domain/simulation/exceptions.py` (extend) — `InvalidSimulationParameterError`, `InvalidSimulationTransition`, `SimulationRuntimeError`.
- `tests/unit/domain/simulation/test_simulation_run.py` — happy path + sad params + all 7 forbidden transitions + RNG-raises edge case.
