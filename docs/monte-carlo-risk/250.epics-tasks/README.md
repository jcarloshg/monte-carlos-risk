# Initiative Index — monte-carlo-risk

> Phase: **250 — Generate Epics & Tasks**
> Initiative path: `docs/monte-carlo-risk/250.epics-tasks/`
> Consumed from: `00.defining.md` (Defining), `100.planning/*` (Planning), `200.designing/*` (Design)
> Produced on: 2026-06-23
> Owner: jcarloshg

This index lists every Epic and every sub-task in execution order. Task IDs are **initiative-wide** and sequential — they do not restart at 001 inside each Epic.

---

## Epic Backlog (sequence-ordered)

| #   | Epic                                                       | Primary Bounded Context       | Sequence Role | Status | Success Metric                                                                                                                     |
| --- | ---------------------------------------------------------- | ----------------------------- | ------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| 001 | **Tracer Bullet — Path to Production**                     | (cross-cutting: scaffold)     | Tracer Bullet | Ready  | `docker compose run monte-carlo describe-mock-data` exits 0 with valid JSON on a clean clone.                                      |
| 002 | **Portfolio — Declare and Validate Holdings**              | Portfolio                     | Foundation    | Ready  | `validate-portfolio portfolio.yaml` exits 0 on valid input and exits 2 on invalid input with a canonical JSON error.               |
| 003 | **Simulation — Generate Risk Paths from Market Data**      | Simulation                    | Foundation    | Ready  | `simulate --portfolio p.yaml` produces a deterministic `PathSet` from mock data; bit-identical on re-run with same seed.           |
| 004 | **Risk Metrics — Compute Tail Risk and Drawdowns**         | RiskMetrics                   | Value         | Ready  | VaR/CVaR/drawdown statistics in `report.json` agree with closed-form formulas on a synthetic normal-return path set.               |
| 005 | **Visualization — Render Risk Charts**                     | Visualization                 | Value         | Ready  | Three deterministic PNGs (`paths.png`, `drawdown.png`, `fan_chart.png`) appear in `--output-dir` and are byte-identical on re-run. |
| 006 | **Run Pipeline — Orchestrate End-to-End with Determinism** | (cross-cutting: orchestrator) | Cross-cutting | Ready  | Full `simulate` run meets NFR-1 (P50 ≤ 10 s, P95 ≤ 30 s on a modern laptop), NFR-4 (byte-identical re-run), NFR-5 (idempotent).    |

---

## Total Task Count

**28 sub-tasks** across 6 Epics. Sized for one developer (jcarloshg) at a typical cycle time of ~1 PR/day; full backlog estimates **6–10 sprints** depending on review latency.

Per-Epic task counts:

| Epic                           | Tasks | Range         |
| ------------------------------ | ----- | ------------- |
| 001 — Tracer Bullet            | 4     | task-001..004 |
| 002 — Portfolio                | 5     | task-005..009 |
| 003 — Simulation + Market Data | 7     | task-010..016 |
| 004 — RiskMetrics              | 4     | task-017..020 |
| 005 — Visualization            | 4     | task-021..024 |
| 006 — Run Pipeline / Quality   | 4     | task-025..028 |

---

## Slicing Strategy

- **Tracer Bullet** (Epic 001) — first per Step 2.3 of the playbook. Small business value but exercises the entire vertical: source layout, CI, Docker, hexagonal tree, structlog, error envelope.
- **Domain-Driven slicing** for Epics 002–005 — one bounded context per Epic, mirroring the four contexts from the frozen Domain Map (`100.planning/01.planning.md` §1).
- **Cross-cutting** Epic 006 — assembles the orchestrator and quality gates (observability, determinism, benchmarks, E2E) that wrap the contexts.

---

## Anti-Patterns Explicitly Rejected

| Anti-pattern                      | How it was rejected in this initiative                                                                                                                                                  |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Horizontal Technical Epic**     | Rejected. Every Epic ships a working CLI command end-to-end. No "Database Migration Epic" or "API Epic."                                                                                |
| **Orphaned Ticket**               | Rejected. Every task has a `Depends on:` field referencing a prior task ID; the dependency graph is committed at `dependency-graph.md`.                                                 |
| **Vague Epic**                    | Rejected. Every Epic §1 has a quantified success metric and every §4 has quantified NFRs traceable to `100.planning/01.planning.md` §2.                                                 |
| **Mega-Epic**                     | Rejected. Each Epic fits in 2–4 sprints (or 1 for a single developer at the educational scope).                                                                                         |
| **Orphaned Out-of-Scope**         | Rejected. Every Epic §3 lists deferred work explicitly; the consolidated register is `out-of-scope.md`.                                                                                 |
| **Acronym Soup Epic**             | Rejected. Epic names use business vocabulary, not tech (e.g., "Portfolio — Declare and Validate Holdings" not "DDD Aggregate Layer 2").                                                 |
| **Tracer Bullet Skip**            | Rejected. Epic 001 is the first Epic and ships a working `describe-mock-data` command.                                                                                                  |
| **Full-Stack Single Commit**      | Rejected. Every task is one PR ≈ 300 LOC max. Layer 3 tasks wait for their Layer 2 dependencies.                                                                                        |
| **Happy-Path-Only AC**            | Rejected. Every task has Happy + Sad + mandatory Edge Case scenarios.                                                                                                                   |
| **Testing the UI**                | N/A — CLI only, no UI. BDD statements assert exit codes, stdout JSON shape, stderr error envelope, and filesystem artifacts.                                                            |
| **Resume-Driven Layer Selection** | Rejected. No Kafka, no CQRS, no feature-flag service. Every Layer-5 item (Delivery) explicitly says `N/A — single-process educational tool, no production rollout needed` (or similar). |

---

## Path-Convention Note

The playbooks default to `.docs/250.epics/` at the repo root. This project keeps its phase artifacts under `docs/monte-carlo-risk/<NNN.phase>/` (mirroring the existing `100.planning/` and `200.designing/` folders) for consistency. The inner structure (`epic-NNN-{slug}/epic.md`, `task-NNN-{slug}/task.md`, `README.md`, `dependency-graph.md`, `out-of-scope.md`) matches the playbook exactly.

---

## Quick-Reference Summary

### Mission
Translate the frozen Planning + Design artifacts into an execution-ready Epic + task backlog of **28 PR-sized sub-tasks across 6 vertically-sliced Epics** (1 Tracer Bullet + 4 Domain-Driven contexts + 1 Cross-cutting Run Pipeline). Every task carries BDD acceptance criteria (Happy + Sad + mandatory Edge Case), a `Depends on:` pointer, and a single owner, so the single-developer team can ship the path-to-prod in the Tracer Bullet and then assemble each context behind a working CLI command without re-deciding architecture.

### Key Decisions
- **Tracer Bullet first** (Epic 001) — exercises hexagonal tree, CI, Docker, structlog, and the canonical error envelope with one trivial `describe-mock-data` command. Every later Epic moves ~10× faster because the path-to-prod exists.
- **Domain-Driven slicing** for Epics 002–005 — one bounded context per Epic (Portfolio → Simulation → RiskMetrics → Visualization).
- **Cross-cutting Epic last** (Epic 006) — orchestrator, structlog event wiring, determinism, idempotency, benchmark, E2E.
- **Sequential task IDs** across the whole initiative (`task-001..task-028`) — enables flat dependency graph.
- **Layer-3 tasks wait for Layer-2 dependencies** — `RunSimulation` orchestrator extensions in tasks 015, 020, 024 each wait on their respective context's domain aggregate.
- **Layer-5 explicitly N/A in most tasks** — no production deployment for an educational single-process CLI; the "delivery" surface is the Docker image + one-command bootstrap, owned by Epic 001.
- **Anti-patterns rejected**: see table above.

### Critical Artifacts
- `README.md` (this file) — initiative index
- `dependency-graph.md` — flat task dependency map (the source of truth for execution order)
- `out-of-scope.md` — consolidated deferred work register (becomes v2 backlog)
- `epic-001-tracer-bullet-path-to-production/epic.md` + 4 tasks
- `epic-002-portfolio-declare-and-validate-holdings/epic.md` + 5 tasks
- `epic-003-simulation-generate-risk-paths/epic.md` + 7 tasks
- `epic-004-risk-metrics-compute-tail-risk/epic.md` + 4 tasks
- `epic-005-visualization-render-risk-charts/epic.md` + 4 tasks
- `epic-006-run-pipeline-quality/epic.md` + 4 tasks

### Open Blockers
_None._ All seven Step-1 inputs were present or explicitly N/A (UI/UX is N/A per ADR-005; documented in every Epic §5).

### Next-Phase Handoff (300 — Coding)
The Coding phase consumes:
- **Per-task `task.md` files** (28 total) — each defines one PR with BDD AC, `Depends on:`, owner, layer tag, and Task-Breakdown checklist.
- **Dependency graph** (`dependency-graph.md`) — for sprint planning; no task can be picked up before its `Depends on:` is merged.
- **Frozen contracts** (from `100.planning/contracts/`) — `cli-contract.yaml` (CLI surface) and `events.schema.json` (event payload shapes) are the authoritative inputs for tasks in Epics 001, 002, 003, and 006.
- **Frozen ADRs** (from `100.planning/adr/` and `200.designing/adr/`) — every task must obey the layer rules from ADR-001/ADR-007 (no forbidden imports in `domain/`) and ADR-012 (deterministic RNG).
- **Bounded-context vocabulary** (from `100.planning/01.planning.md` §1) — task AC and code identifiers use Ubiquitous Language verbatim.
- **Single-owner convention** — every task names `Owner: jcarloshg`. No anonymous tickets.
