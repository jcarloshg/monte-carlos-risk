# Epic 005: Visualization — Render Risk Charts

**Status:** Ready
**Bounded Context:** Visualization
**Sequence Order:** 5 of 6 (Value)
**Estimated Sprints:** 1

> Renders the headline risk numbers as PNG charts the user can look at. The first time a user "sees" the output of the tool. Deterministic per ADR-012 §Determinism for non-numpy operations.

## 1. Business Context & Value

- **Why are we building this?** Quant reports without charts are half-finished. Three standard charts (`paths.png`, `drawdown.png`, `fan_chart.png`) communicate the distribution shape, the worst-case drawdown, and the uncertainty band over time — visually and instantly.
- **Success Metrics:**
  - All three PNGs are written to `--output-dir` on every successful `simulate` run.
  - PNGs are **byte-identical** across re-runs with identical inputs (NFR-4 + ADR-012 determinism guarantees).
  - Visualization adds **≤ 1 s** to a default run (asserted in `task-027`).

## 2. Architectural Scope (C4 Level 2)

- **Containers Touched:** `ChartArtifact` aggregate (`domain/visualization/`); `MatplotlibRenderer` adapter (`infrastructure/rendering/`); `FilesystemOutputWriter` adapter (`infrastructure/filesystem/`); `RunSimulation` orchestrator extended (`application/use_cases/`).
- **External Dependencies:** matplotlib (whitelisted in `infrastructure/` per ADR-001; forbidden in `domain/`).
- **Database Impact:** None.

## 3. Strict "Out of Scope"

- **Interactive charts** (Plotly, Bokeh, Streamlit) — v2.
- **Multiple chart themes** — v1 uses one pinned `rcParams` set for determinism.
- **PDF / SVG export** — v1 emits PNG only.
- **Chart annotations** (e.g., "this is the 95% VaR line") — v1 minimal labeling only.
- **Web dashboard** — N/A per ADR-005.

## 4. Non-Functional Requirements (NFRs)

- **NFR-1:** Visualization adds ≤ 1 s to default run.
- **NFR-4 / NFR-5:** PNGs are byte-identical across re-runs. ADR-012 §Determinism for non-numpy operations mandates Agg backend, pinned rcParams, Pillow metadata stripping.
- **NFR-3:** `domain/visualization/` has zero forbidden imports (matplotlib lives in `infrastructure/`).

## 5. Required Technical Artifacts (Definition of Ready)

- [ ] C4 Container Diagram approved. ✅
- [ ] CLI contract section approved. ✅ `cli-contract.yaml` §`schemas.simulation_report.artifacts` lists the four artifact paths.
- [ ] UI/UX designs approved. **N/A — CLI-only per ADR-005.**
- [ ] Event schemas merged. ✅ `ChartsRendered` payload (the list of `ChartArtifact`s) is frozen.

## 6. User Stories (BDD)

- **Story 5.1:** Three deterministic PNGs appear in `--output-dir`.
  - *Scenario:* `Given` a successful simulate run, `When` I inspect `./output/`, `Then` three PNGs exist (`{run_id}_paths.png`, `{run_id}_drawdown.png`, `{run_id}_fan_chart.png`) plus `{run_id}_report.json`.
  - *Edge Case placeholder:* handled in `task-024`.
- **Story 5.2:** PNGs are byte-identical across re-runs.
  - *Scenario:* `Given` a first run completed, `When` I re-run with identical `--seed` and other inputs, `Then` the PNGs are byte-identical to the first run's (NFR-4 + ADR-012 determinism).
  - *Edge Case placeholder:* handled in `task-026`.
- **Story 5.3:** Renderer failure surfaces as a typed exception.
  - *Scenario:* `Given` `--output-dir` is read-only, `When` I run `simulate`, `Then` exit code is 6 and `error_code = "visualization_failed"` (or `output_dir_not_writable` — whichever is detected first).
  - *Edge Case placeholder:* handled in `task-022`/`task-024`.
