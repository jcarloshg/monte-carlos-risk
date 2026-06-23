# Task 025 — structlog Event Wiring (Full Observability)

**Epic:** epic-006-run-pipeline-quality
**Layer:** Observability
**Sprint:** 07
**Depends on:** task-024
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## Context

`StructlogEventSink` was a stub since `task-009`. Now it must emit exactly one JSON line per domain event with `run_id`, `event_name`, and the validated payload. Also adds per-event timing logs. Traces to Story 6.1.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a simulate run, `When` I capture stderr, `Then` I see exactly six structlog JSON lines (one per event) in the canonical order from `events.schema.json` §invariants, each with `event` ∈ {`PortfolioDefined`, `MarketDataLoaded`, `SimulationStarted`, `SimulationCompleted`, `RiskMetricsCalculated`, `ChartsRendered`}, `run_id` matching across all six, and a `payload` field validated against the event's JSON Schema.
- [ ] **Scenario 2 (Sad Path):** Given the orchestrator raises an exception mid-pipeline (e.g., `RiskMetricsFailed`), `When` I capture stderr, `Then` I see the events emitted up to the failure point, plus one additional `level = "error"` log line with the typed exception class name and a structured `context` dict. The success-path event sequence is not continued.
- [ ] **Edge Case (Mandatory):** If the terminal is a TTY, logs are formatted as colored text for human readability; if non-TTY (CI), logs are single-line JSON. A test asserts both modes by setting `STRUCTLOG_FORCE_JSON=1` and `STRUCTLOG_FORCE_JSON=0` and verifying the captured output shape.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A — structlog config is internal.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** This task IS the metrics/logs deliverable.
- [ ] **Contract Tests:** N/A — first event-schema validation test in `task-026`.

## Out of Scope

- Datadog / OpenTelemetry / any APM tool — N/A per NFR-8 ($0/mo).
- The benchmark gate (`task-027`).
- The E2E smoke (`task-028`).

## Deliverables

- Full implementation in `src/monte_carlo_risk/infrastructure/logging/structlog_event_sink.py` — emits structured logs with `event`, `run_id`, `payload`, `timestamp`, `level`.
- `src/monte_carlo_risk/interface/logging.py` (extend) — `MPL_DETERMINISTIC_RCPARAMS` already lives here; add TTY detection via `sys.stderr.isatty()` and `STRUCTLOG_FORCE_JSON` env override.
- Per-event timing: each orchestrator step wraps its work in a `structlog.contextvars.bind_contextvars` block and emits `event_completed` with `duration_seconds`.
- `tests/unit/infrastructure/logging/test_structlog_event_sink.py` — happy + sad + TTY-detection edge case.
- `tests/infrastructure/logging/test_log_format_json.py` — asserts every emitted line is valid JSON in non-TTY mode.
