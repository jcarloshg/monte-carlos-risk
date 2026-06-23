# Task 022 — `MatplotlibRenderer` Adapter

**Epic:** epic-005-visualization-render-risk-charts
**Layer:** Infrastructure
**Sprint:** 06
**Depends on:** task-021
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 350 LOC

## Context

Implements the `ChartRenderer` Protocol from `application/ports/chart_renderer.py`. Takes a `ChartArtifact` and writes a PNG to a `Path`. Uses matplotlib's Agg backend (set in `conftest.py` before any matplotlib import) with a pinned `rcParams` set for determinism per ADR-012.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a valid `ChartArtifact(kind=Paths, ...)`, `When` I call `MatplotlibRenderer().render(artifact, output_path)`, Then a PNG file exists at `output_path` and is non-empty.
- [ ] **Scenario 2 (Sad Path):** Given `output_path` is in a non-existent directory (parent dir doesn't exist), `When` I call `render`, Then `VisualizationFailed` is raised wrapping the underlying matplotlib exception.
- [ ] **Edge Case (Mandatory):** Given two `render` calls with identical inputs in sequence, `When` I `sha256`-hash both PNGs, `Then` the hashes are equal (byte-identical determinism per ADR-012 §matplotlib rendering mitigations: Agg backend + pinned rcParams + Pillow metadata stripping).

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** Adds `tests/contract/test_chart_renderer_contract.py` — parameterized against any `ChartRenderer`; asserts (a) renders produce a non-empty file and (b) byte-identical inputs produce byte-identical outputs.

## Out of Scope

- The `FilesystemOutputWriter` (used to write the JSON report; `task-023`).
- The orchestrator extension (`task-024`).
- Multiple chart themes or formats.

## Deliverables

- `src/monte_carlo_risk/infrastructure/rendering/matplotlib_renderer.py` — `class MatplotlibRenderer` implementing `ChartRenderer`. Internal helpers for each `ChartKind` (3 small private functions: `_render_paths`, `_render_drawdown`, `_render_fan_chart`).
- `src/monte_carlo_risk/infrastructure/rendering/rcparams.py` — pinned `MPL_DETERMINISTIC_RCPARAMS` dict (no random styles, fixed DPI, fixed figure size, etc.).
- `src/monte_carlo_risk/infrastructure/rendering/metadata_strip.py` — Pillow-based helper to strip PNG metadata timestamps.
- `tests/conftest.py` — sets `matplotlib.use("Agg")` before any pyplot import; loads `MPL_DETERMINISTIC_RCPARAMS`.
- `src/monte_carlo_risk/domain/visualization/exceptions.py` (extend) — `VisualizationFailed`.
- `tests/unit/infrastructure/rendering/test_matplotlib_renderer.py` — happy + sad + byte-identical determinism edge case.
- `tests/contract/test_chart_renderer_contract.py` — first cross-implementation contract test.
