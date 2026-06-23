# Task 016 — `simulate` CLI Command Extension

**Epic:** epic-003-simulation-generate-risk-paths
**Layer:** Transport
**Sprint:** 04
**Depends on:** task-015
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 300 LOC

## Context

Wires the `simulate` command per `cli-contract.yaml` §`commands[simulate]`. The composition root in `interface/cli/app.py` registers the command, wires `MockMarketDataSource` + `NumpyRNG` + `CsvReturnMatrixLoader` as defaults, and writes the partial `simulation_report.json` to `--output-dir` (no PNGs yet — those land in `task-024`). Traces to Stories 3.1, 3.2.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a valid portfolio, `When` I run `monte-carlo simulate --portfolio p.yaml --seed 1729 --n-paths 10000 --horizon 252`, `Then` exit code is 0, stdout is a JSON document matching `simulation_report` (with `path_set_summary` populated and `risk_report` + `artifacts` absent or null), and `{run_id}_report.json` is written to `./output`.
- [ ] **Scenario 2 (Sad Path):** Given `--provider http` (v2 stub), `When` I run the command, `Then` exit code is 3 (per `cli-contract.yaml`) and the canonical error is `error_code = "provider_not_implemented"` with `context.provider = "http"`.
- [ ] **Scenario 3 (Reproducibility):** Given two consecutive runs with identical `--seed` and other inputs, `Then` the `simulation_report.json` outputs are byte-identical (the `run_id` field is `auto` by default — recorded separately in the artifact filename, NOT in the JSON's run_id, to preserve byte-identical reproducibility per NFR-5).
- [ ] **Edge Case (Mandatory):** If `--output-dir` is not writable (e.g., a read-only mount), exit code is 6 and `error_code = "output_dir_not_writable"` with the resolved path in `context`. The error is detected BEFORE running the simulation (cheap check, not after minutes of compute).

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** Adds the `simulate` Typer subcommand per the frozen `cli-contract.yaml` v1.0.0 contract.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** `--provider` flag has values `mock` (default) and `http` (v2 stub). Acts as a runtime switch, not a feature flag service.
- [ ] **Metrics / Logs:** Per-event structlog logging wired through `StructlogEventSink` (extended from `task-009`).
- [ ] **Contract Tests:** Extends `tests/contract/test_cli_help_matches_contract.py` to cover the `simulate` command's flags.

## Out of Scope

- Risk metrics computation (Epic 004).
- PNG output (Epic 005 / `task-024`).
- The full end-to-end determinism test (`task-026`).

## Deliverables

- `src/monte_carlo_risk/interface/cli/commands/simulate.py` — Typer command implementing all flags from `cli-contract.yaml` §`commands[simulate]`.
- `src/monte_carlo_risk/infrastructure/market_data/http_market_data_source.py` — `class HttpMarketDataSource` raising `NotImplementedError("v2 — gated by Spike S-001")`, marked `@pytest.mark.xfail(reason="v2")`.
- Extension to `src/monte_carlo_risk/interface/cli/app.py` — wire composition root with `MockMarketDataSource`, `NumpyRNG`, `CsvReturnMatrixLoader`, `RunSimulation`, `simulate` command.
- `tests/integration/interface/test_simulate_e2e.py` — runs the CLI as a subprocess for happy + sad + reproducibility scenarios.
- Extension to `tests/contract/test_cli_help_matches_contract.py` for `simulate` flags.
