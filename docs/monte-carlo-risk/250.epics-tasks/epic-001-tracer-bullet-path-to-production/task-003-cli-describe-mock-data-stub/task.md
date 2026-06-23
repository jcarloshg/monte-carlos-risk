# Task 003 — CLI `describe-mock-data` Stub + Error Envelope + structlog

**Epic:** epic-001-tracer-bullet-path-to-production
**Layer:** Transport
**Sprint:** 01
**Depends on:** task-002
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 300 LOC

## Context

The Tracer Bullet's one working end-to-end command. Wires the Typer CLI root, the canonical JSON error envelope (matching `cli-contract.yaml` §`error_schema`), and the structlog setup that every later task depends on. The actual mock data is a hardcoded stub; the real corpus lands in Epic 003 / task-010. Traces to Story 1.2.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given the CLI is installed, When I run `monte-carlo describe-mock-data`, Then exit code is 0 and stdout is a JSON document matching `mock_data_descriptor` schema (`provider: "mock"`, `version: "0.1.0-stub"`, `tickers: []`, `date_range: {start: null, end: null}`, `frequency: "daily"`).
- [ ] **Scenario 2 (Sad Path):** Given the user passes an unknown flag `--bogus`, When I run `monte-carlo describe-mock-data --bogus`, Then exit code is 2 and stderr contains exactly one canonical JSON error line matching `error_schema` with `error_code = "cli_argument_error"` (new code, added to enum in `cli-contract.yaml`).
- [ ] **Edge Case (Mandatory):** If `structlog` is configured for JSON output and the user's terminal is non-TTY (e.g., CI), every event emitted to stderr must be valid JSON on a single line — no multi-line stack traces or colored output. A unit test asserts this by capturing stderr and parsing each line as JSON.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** Adds `describe-mock-data` CLI command. Frozen in `100.planning/contracts/cli-contract.yaml` v1.0.0 — no contract change required for this task.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** Adds structlog configuration (`src/monte_carlo_risk/interface/logging.py`). No metric emission yet.
- [ ] **Contract Tests:** N/A — first contract test lands with Epic 002 / task-009.

## Out of Scope

- The `simulate` and `validate-portfolio` commands (Epics 002, 003).
- Real mock CSV corpus (Epic 003 / task-010).
- Actual event emission from the orchestrator (Epic 006 / task-025).

## Deliverables

- `src/monte_carlo_risk/interface/cli/app.py` — Typer root with `describe-mock-data` command (and a `--help` smoke test target).
- `src/monte_carlo_risk/interface/cli/commands/describe_mock_data.py` — command implementation returning a hardcoded stub matching `mock_data_descriptor`.
- `src/monte_carlo_risk/interface/errors.py` — `CanonicalCliError` dataclass + `emit_canonical_error(error_code, message, context, run_id)` function.
- `src/monte_carlo_risk/interface/logging.py` — structlog configuration with JSON renderer, `--log-level` and `--log-format` global flags.
- `src/monte_carlo_risk/interface/cli_contract.py` — argparse/Typer validators matching the flags section of `cli-contract.yaml`.
- New `error_code` value `"cli_argument_error"` added to `cli-contract.yaml` §`error_schema` enum (contract minor version bump `v1.1.0` — recorded in this task's commit message).
- `tests/unit/interface/test_canonical_error.py` — asserts the emitted JSON matches `error_schema` exactly.
- `tests/unit/interface/test_describe_mock_data.py` — asserts happy-path JSON output.
