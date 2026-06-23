# Task 008 — `validate-portfolio` Use Case

**Epic:** epic-002-portfolio-declare-and-validate-holdings
**Layer:** Application
**Sprint:** 02
**Depends on:** task-007
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 200 LOC

## Context

The first application-layer use case. Pure orchestration: takes a portfolio source (path or inline string), dispatches to the right parser, returns a `PortfolioValidationReport`. Emits the `PortfolioDefined` event on success. Traces to all three Stories.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a valid YAML portfolio, When `ValidatePortfolio(portfolio_source=Path("p.yaml")).execute()`, Then the result is `PortfolioValidationReport(valid=True, errors=[], portfolio=<echo>)` and a `PortfolioDefined` event is emitted via the orchestrator's event sink (a Protocol injected as `event_sink`).
- [ ] **Scenario 2 (Sad Path):** Given an invalid portfolio (weights don't sum), When `execute()`, Then the result is `PortfolioValidationReport(valid=False, errors=[{code: "weights_sum_must_equal_one", message: "..."}], portfolio=<empty echo>)` and NO `PortfolioDefined` event is emitted.
- [ ] **Edge Case (Mandatory):** If `event_sink.emit()` raises (e.g., the test passes a sink that always raises), `execute()` MUST NOT swallow the exception — the use case surfaces it so the CLI can convert to a canonical error. This prevents silent event-emission failures.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A — no CLI command added in this task.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** One `structlog` info log per validation (`portfolio.validated` or `portfolio.invalid`) — uses the `event_sink` Protocol, not direct structlog calls (defer the concrete sink to `task-025`).
- [ ] **Contract Tests:** N/A — first contract test in `task-009`.

## Out of Scope

- The `validate-portfolio` CLI command (`task-009`).
- The `simulate` orchestrator (`task-015`) — `validate-portfolio` is a standalone use case.

## Deliverables

- `src/monte_carlo_risk/application/use_cases/validate_portfolio.py` — `class ValidatePortfolio(parsers: dict[str, PortfolioParser], event_sink: EventSink)` with `execute(source: PortfolioSource) -> PortfolioValidationReport`.
- `src/monte_carlo_risk/application/portfolio_source.py` — `PortfolioSource` Protocol with `kind: Literal["path", "inline"]` + value.
- `src/monte_carlo_risk/application/portfolio_validation_report.py` — `@dataclass(frozen=True) class PortfolioValidationReport(valid: bool, errors: tuple[ValidationError, ...], portfolio: Portfolio | None)`.
- `src/monte_carlo_risk/application/ports/event_sink.py` — `class EventSink(Protocol)` with `emit(event: DomainEvent) -> None`.
- `tests/unit/application/use_cases/test_validate_portfolio.py` — happy + sad + event-emission + event-sink-raises edge case.
