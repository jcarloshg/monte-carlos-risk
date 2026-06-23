# ADR-008 — Structlog with JSON Renderer for Structured stderr Observability

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Source inputs:** `docs/00.defining.md` 300-Q6.1, 300-Q6.2, 300-Q6.5

## Context

Logs must be machine-parseable for `docker compose logs` consumption and
future log aggregation. The defining doc requires the canonical fields
(`timestamp`, `level`, `correlationId`, `service`, `version`, `runId`)
on every line.

## Options Considered

1. **`logging` stdlib with custom Formatter.** Verbose, easy to drift on
   the formatter.
2. **structlog with JSON renderer.** Declarative, type-friendly
   (`structlog.stdlib.LoggerFactory`), one config file.
3. **`loguru`.** Convenient API but adds a runtime dependency that
   monkey-patches `logging`. Worse fit for `mypy --strict`.

## Decision

**Option 2.** `structlog` configured in `src/interfaces/cli/logging_setup.py`
with `JSONRenderer` to stderr. Required processors (in order):

1. `add_log_level`
2. `TimeStamper(fmt="iso", utc=True)`
3. `StackInfoRenderer`
4. `format_exc_info`
5. `JSONRenderer`

A `bind_contextvars(correlationId=..., runId=...)` call at the CLI entry
point propagates the IDs through every downstream log line within the
process. `correlationId` is generated at CLI startup (`uuid4`); `runId` is
assigned when `SimulationRun` is created.

## Consequences

**Positive**
- One JSON object per line. `docker compose logs | jq` works.
- `correlationId` ties every log line to a run and a CLI invocation,
  matching Defining 300-Q6.5.
- `structlog.testing.capture_logs()` makes log-shape assertions trivial
  in tests.

**Negative**
- `structlog` is one more dependency. Well-maintained, small footprint.

**Reversibility**
- Trivial — swap the renderer for `ConsoleRenderer` for local dev.
