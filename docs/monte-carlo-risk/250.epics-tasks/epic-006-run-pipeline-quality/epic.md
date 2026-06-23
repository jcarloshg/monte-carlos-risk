# Epic 006: Run Pipeline — Orchestrate End-to-End with Determinism

**Status:** Ready
**Bounded Context:** (cross-cutting: orchestrator + observability + quality)
**Sequence Order:** 6 of 6 (Cross-cutting)
**Estimated Sprints:** 1

> Closes the initiative. Wires full structlog observability across all six events, asserts end-to-end determinism + idempotency (NFR-4, NFR-5), installs the NFR-1 benchmark gate, and ships the Docker E2E smoke + golden-file test that proves "clean clone to green run in ≤ 5 min."

## 1. Business Context & Value

- **Why are we building this?** Epics 001–005 ship the path-to-prod and each context end-to-end. Epic 006 is the **quality net** that turns the project from "it works on my machine" into "it provably works the same way every run, on every supported machine."
- **Success Metrics:**
  - **NFR-1 (latency budget):** default run `simulate` P50 ≤ 10 s, P95 ≤ 30 s — asserted as a CI benchmark gate that fails the build on regression.
  - **NFR-4 (reproducibility):** byte-identical re-run test passes in CI on the pinned Linux image.
  - **NFR-5 (idempotency):** two consecutive runs with identical inputs produce byte-identical `simulation_report.json` + 3 PNGs.
  - **NFR-7 (bootstrap):** Docker E2E smoke + golden file passes in CI; README documents the procedure.

## 2. Architectural Scope (C4 Level 2)

- **Containers Touched:** `StructlogEventSink` (full wiring, was stubbed in `task-009`); end-to-end `RunSimulation` integration; CI workflow extensions; Docker E2E test.
- **External Dependencies:** pytest-benchmark, structlog, pytest-regressions (for golden-file comparison).
- **Database Impact:** None.

## 3. Strict "Out of Scope"

- **Production deployment / canary / feature flags** — single-process educational tool, no production rollout surface.
- **Shift-right synthetic monitoring** — no production environment to monitor.
- **Cross-platform byte-identical reproducibility** — asserted per-platform (CI Linux image only). macOS / Windows best-effort.
- **Cloud cost monitoring** — $0/mo (NFR-8) structurally enforced; no spend to monitor.

## 4. Non-Functional Requirements (NFRs)

All NFRs from `100.planning/01.planning.md` §2 are exercised by this Epic:

- **NFR-1:** latency budget — `task-027`.
- **NFR-2:** test suite budgets — `task-026` + `task-027` must finish within budget.
- **NFR-4 / NFR-5:** reproducibility + idempotency — `task-026`.
- **NFR-6:** error contract — verified by every task's Sad Path scenarios throughout the initiative; final consolidated check in `task-028`.
- **NFR-7:** one-command bootstrap — `task-028`.
- **NFR-8:** cost ceiling — structurally enforced (no cloud); `task-028` confirms via Docker build.

## 5. Required Technical Artifacts (Definition of Ready)

- [ ] C4 Container Diagram approved. ✅
- [ ] CLI contract section approved. ✅ (all commands + schemas + error_schema are frozen)
- [ ] UI/UX designs approved. **N/A — CLI-only per ADR-005.**
- [ ] Event schemas merged. ✅ (all 6 events frozen)

## 6. User Stories (BDD)

- **Story 6.1:** Every domain event produces a structured JSON log line.
  - *Scenario:* `Given` a simulate run, `When` I inspect stderr, `Then` I see exactly six structlog JSON lines, one per event, in canonical order, each with `event` and `run_id` fields and the payload validated against `events.schema.json`.
  - *Edge Case placeholder:* handled in `task-025`.
- **Story 6.2:** Two consecutive runs with identical inputs produce byte-identical artifacts.
  - *Scenario:* `Given` a first run completed, `When` I re-run with the same `--seed` and other inputs, `Then` the `simulation_report.json` + 3 PNGs are byte-identical to the first run's (modulo `run_id`, which is excluded from the JSON's run_id field per `task-016`'s convention).
  - *Edge Case placeholder:* handled in `task-026`.
- **Story 6.3:** Default-run latency meets NFR-1.
  - *Scenario:* `Given` the CI benchmark, `When` pytest-benchmark runs `simulate` 10 times, `Then` median ≤ 10 s and 95th percentile ≤ 30 s.
  - *Edge Case placeholder:* handled in `task-027`.
- **Story 6.4:** Clean clone → Docker → green E2E.
  - *Scenario:* `Given` a clean git clone on a Linux CI runner, `When` `docker compose run --rm monte-carlo simulate --portfolio tests/fixtures/valid_portfolio.yaml --seed 1729` runs, `Then` exit code is 0 and the output matches the golden file in `tests/fixtures/golden/`.
  - *Edge Case placeholder:* handled in `task-028`.
