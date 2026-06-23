# Epic 003: Simulation — Generate Risk Paths from Market Data

**Status:** Ready
**Bounded Context:** Simulation
**Sequence Order:** 3 of 6 (Foundation)
**Estimated Sprints:** 2

> The Monte Carlo engine itself. Loads bundled mock market data, generates N independent portfolio paths via a deterministic RNG, and produces a `PathSet`. Closes the gap from "Portfolio validated" to "we have paths to measure risk on" — the prerequisites for Epic 004 (RiskMetrics).

## 1. Business Context & Value

- **Why are we building this?** Without paths, there is nothing to measure risk on. This Epic is the heart of the tool: reproducible (NFR-4), deterministic (NFR-4), vectorized (NFR-1 P50 ≤ 10 s).
- **Success Metrics:**
  - `monte-carlo simulate --portfolio p.yaml --n-paths 10000 --horizon 252 --seed 1729` produces a `simulation_report.json` whose `path_set` summary (terminal wealth percentiles, max drawdown percentiles) is **bit-identical** to a second run with the same inputs (NFR-4, NFR-5).
  - The full simulation (Portfolio → MDS → Sim, no risk/charts yet) finishes in **P50 ≤ 8 s, P95 ≤ 25 s** on a modern laptop with default settings (margin under the NFR-1 10 s/30 s budget to leave headroom for RiskMetrics + Visualization in Epic 006).
  - State machine violations (`Running → Pending`, etc.) raise `InvalidSimulationTransition` per `state-machine-simulation-run.md`.

## 2. Architectural Scope (C4 Level 2)

- **Containers Touched:** `MockMarketDataSource`, `CsvReturnMatrixLoader`, `NumpyRNG` (all `infrastructure/`); `SimulationRun` aggregate + state machine (`domain/simulation/`); `RunSimulation` orchestrator stub extended (`application/use_cases/`); `simulate` CLI command (`interface/cli/commands/`).
- **External Dependencies:** numpy (whitelisted in `domain/` per ADR-002). Bundled CSV corpus is checked-in git data, not a runtime dependency.
- **Database Impact:** None.

## 3. Strict "Out of Scope"

- **Risk metrics computation** — Epic 004.
- **Chart rendering** — Epic 005.
- **Real market-data adapter (HttpMarketDataSource)** — v2 (Spike S-001).
- **Variance reduction** (antithetic, control variates) — v2.
- **Multi-threaded path generation** — v2.
- **Persistent run history** — v2 (ADR-009).

## 4. Non-Functional Requirements (NFRs)

- **NFR-1:** Simulation step (only) P50 ≤ 8 s, P95 ≤ 25 s for defaults (asserted as a benchmark gate in `task-027`).
- **NFR-4:** Deterministic — same `(seed, portfolio, n_paths, horizon, mock_data_version)` → identical `PathSet`.
- **NFR-5:** Idempotent CLI — re-running with identical inputs produces identical artifacts (asserted by byte-comparison test in `task-026`).
- **NFR-3:** `domain/simulation/` has zero forbidden imports (linter passes).

## 5. Required Technical Artifacts (Definition of Ready)

- [ ] C4 Container Diagram approved. ✅
- [ ] CLI contract section approved. ✅ `cli-contract.yaml` §`commands[simulate]` (all flags) and §`schemas.simulation_report` are frozen.
- [ ] UI/UX designs approved. **N/A — CLI-only per ADR-005.**
- [ ] Event schemas merged. ✅ `MarketDataLoaded`, `SimulationStarted`, `SimulationCompleted` payloads are frozen in `events.schema.json`.

## 6. User Stories (BDD)

- **Story 3.1:** Load bundled mock data and run a simulation end-to-end (without risk metrics or charts).
  - *Scenario:* `Given` the bundled CSV corpus and a valid portfolio, `When` I run `monte-carlo simulate --portfolio p.yaml`, Then a `simulation_report.json` is written to `--output-dir` with a `path_set_summary` block (terminal wealth percentiles, max drawdown percentiles, shape metadata).
  - *Edge Case placeholder:* handled in `task-016`.
- **Story 3.2:** Reproducibility — same inputs yield identical outputs.
  - *Scenario:* `Given` a first run completed, `When` I re-run with `--seed 1729` and identical other inputs, Then the second `simulation_report.json` is byte-identical to the first (modulo run_id, which is auto-generated).
  - *Edge Case placeholder:* handled in `task-026`.
- **Story 3.3:** State machine enforces legal transitions.
  - *Scenario:* `Given` a `SimulationRun` in `Running` state, `When` `start()` is called again, Then `InvalidSimulationTransition` is raised.
  - *Edge Case placeholder:* handled in `task-014`.
