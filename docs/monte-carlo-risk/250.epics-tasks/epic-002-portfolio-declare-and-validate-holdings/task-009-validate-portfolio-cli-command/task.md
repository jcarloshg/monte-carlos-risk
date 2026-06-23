# Task 009 — `validate-portfolio` CLI Command

**Epic:** epic-002-portfolio-declare-and-validate-holdings
**Layer:** Transport
**Sprint:** 02
**Depends on:** task-008
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## Context

Wires the `validate-portfolio` use case to a Typer subcommand. The composition root in `interface/cli/app.py` is extended to register the command and wire the parsers + event sink. Traces to Stories 2.1, 2.2, 2.3. First formal CLI contract test.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given `tests/fixtures/valid_portfolio.yaml`, When I run `monte-carlo validate-portfolio --portfolio tests/fixtures/valid_portfolio.yaml`, Then exit code is 0 and stdout is a JSON document matching `portfolio_validation_report` schema with `valid: true`.
- [ ] **Scenario 2 (Sad Path):** Given `tests/fixtures/invalid_weights.yaml` (sums to 0.95), When I run the command, Then exit code is 2 and stderr is exactly one JSON error with `error_code = "weights_sum_must_equal_one"` and `context.actual_sum = 0.95`.
- [ ] **Scenario 3 (Inline Happy Path):** Given `--portfolio 'AAPL:0.4,MSFT:0.3,GOOG:0.3'`, When I run the command, Then exit code is 0 and stdout matches `portfolio_validation_report`.
- [ ] **Edge Case (Mandatory):** If the YAML file does not exist, exit code is 2 and the canonical error has `error_code = "portfolio_file_not_found"` with the resolved absolute path in `context.path`. The test asserts both the path is absolute (not the user-supplied relative path) and the error code is correct.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** Adds the `validate-portfolio` Typer subcommand. Per `cli-contract.yaml` v1.0.0, this is a previously-declared top-level command — no contract change required.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** Concrete `StructlogEventSink` adapter (in `infrastructure/logging/structlog_event_sink.py`) is wired at the composition root. Replaces the test stub from `task-008`.
- [ ] **Contract Tests:** Adds the first formal CLI contract test — `tests/contract/test_cli_help_matches_contract.py`. Asserts Typer's `--help` output for `validate-portfolio` matches the flags declared in `cli-contract.yaml` §`commands[validate-portfolio]`.

## Out of Scope

- The `simulate` command (Epic 003 / task-016).
- Wiring the orchestrator (`task-015`).
- The full event-emission contract test (Epic 006 / task-026).

## Deliverables

- `src/monte_carlo_risk/interface/cli/commands/validate_portfolio.py` — Typer command function that dispatches to the use case and converts the result to stdout JSON or canonical stderr error.
- Extension to `src/monte_carlo_risk/interface/cli/app.py` — register `validate-portfolio` and wire the composition root.
- `src/monte_carlo_risk/infrastructure/logging/structlog_event_sink.py` — `class StructlogEventSink` implementing `application/ports/event_sink.py`. For now, logs the event name as a structured info log; full wiring lands in `task-025`.
- `tests/fixtures/valid_portfolio.yaml` + `tests/fixtures/invalid_weights.yaml` (committed fixture files).
- `tests/contract/test_cli_help_matches_contract.py` — first CLI contract test.
- `tests/integration/interface/test_validate_portfolio_e2e.py` — runs the CLI as a subprocess and asserts exit codes + stdout/stderr shape.
