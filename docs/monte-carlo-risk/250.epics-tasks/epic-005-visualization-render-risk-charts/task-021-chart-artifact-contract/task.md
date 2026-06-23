# Task 021 — `ChartArtifact` Contract

**Epic:** epic-005-visualization-render-risk-charts
**Layer:** Domain
**Sprint:** 06
**Depends on:** task-019
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## Context

The Visualization aggregate root. Holds the **contract** for what charts exist (`paths`, `drawdown`, `fan_chart`) and what data they need — but does NOT contain any matplotlib code (that's the renderer's job, per ADR-001 / hexagonal). Traces to Story 5.1.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a `RiskReport` + `PathSet`, `When` I call `ChartArtifact.create_for_risk_report(risk_report, path_set, kind="paths")` (and similarly for `drawdown`, `fan_chart`), Then a `ChartArtifact` value object is returned with `kind`, `title`, `data_spec` (a typed dict describing the chart's data needs), and an unset `absolute_path` (filled in after rendering).
- [ ] **Scenario 2 (Sad Path):** Given `kind = "unknown_chart"`, `When` I call the factory, `Then` `InvalidChartKindError` is raised. The valid kinds are exactly the three from the enum.
- [ ] **Edge Case (Mandatory):** `ChartArtifact` is `@dataclass(frozen=True)`. The `data_spec` field contains **only** numpy arrays + scalar metadata — no matplotlib types, no `Path`, no `Figure`, no `Axes`. A static type-check (`mypy --strict`) enforces this; any PR that leaks a matplotlib type into `data_spec` fails CI.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** N/A.

## Out of Scope

- The matplotlib renderer (`task-022`).
- The filesystem output writer (`task-023`).
- The orchestrator extension (`task-024`).

## Deliverables

- `src/monte_carlo_risk/domain/visualization/__init__.py`
- `src/monte_carlo_risk/domain/visualization/chart_kind.py` — `enum class ChartKind(Paths, Drawdown, FanChart)`.
- `src/monte_carlo_risk/domain/visualization/chart_artifact.py` — `@dataclass(frozen=True, slots=True) class ChartArtifact(kind, title, data_spec: dict, absolute_path: Path | None)` with `@classmethod create_for_risk_report(...)`.
- `src/monte_carlo_risk/domain/visualization/events.py` — `ChartsRendered` event class.
- `src/monte_carlo_risk/domain/visualization/exceptions.py` — `InvalidChartKindError`.
- `tests/unit/domain/visualization/test_chart_artifact.py` — happy + sad + data-spec-purity edge case (asserts no matplotlib types).
