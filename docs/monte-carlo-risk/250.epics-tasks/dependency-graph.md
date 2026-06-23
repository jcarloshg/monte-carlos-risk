# Dependency Graph — monte-carlo-risk

> Source of truth for execution order across the initiative.
> Generated: 2026-06-23
> Total tasks: 28

Read top-to-bottom. A task can be picked up only when **every** entry in its `Depends on:` column has been merged.

## Task Table

| Task     | Title                                      | Layer          | Epic | Sprint | Depends on                   | Owner     | Status |
| -------- | ------------------------------------------ | -------------- | ---- | ------ | ---------------------------- | --------- | ------ |
| task-001 | dev-tooling-bootstrap                      | Infra          | 001  | 01     | none                         | jcarloshg | Done   |
| task-002 | shared-kernel-value-objects                | Domain         | 001  | 01     | task-001                     | jcarloshg | Done   |
| task-003 | cli-describe-mock-data-stub                | Transport      | 001  | 01     | task-002                     | jcarloshg |
| task-004 | import-linter-and-ci-pipeline              | Defense        | 001  | 01     | task-003                     | jcarloshg |
| task-005 | portfolio-shared-kernel-extensions         | Domain         | 002  | 02     | task-002                     | jcarloshg |
| task-006 | portfolio-aggregate-and-invariants         | Domain         | 002  | 02     | task-005                     | jcarloshg |
| task-007 | portfolio-yaml-and-inline-parser           | Infrastructure | 002  | 02     | task-006                     | jcarloshg |
| task-008 | validate-portfolio-use-case                | Application    | 002  | 02     | task-007                     | jcarloshg |
| task-009 | validate-portfolio-cli-command             | Transport      | 002  | 02     | task-008                     | jcarloshg |
| task-010 | bundled-mock-csv-corpus                    | Data           | 003  | 03     | task-004                     | jcarloshg |
| task-011 | csv-return-matrix-loader                   | Infrastructure | 003  | 03     | task-010                     | jcarloshg |
| task-012 | mock-market-data-source                    | Infrastructure | 003  | 03     | task-011                     | jcarloshg |
| task-013 | numpy-rng-adapter                          | Infrastructure | 003  | 03     | task-004                     | jcarloshg |
| task-014 | simulation-run-aggregate-and-state-machine | Domain         | 003  | 03     | task-013                     | jcarloshg |
| task-015 | run-simulation-orchestrator-extension      | Application    | 003  | 04     | task-009, task-012, task-014 | jcarloshg |
| task-016 | simulate-cli-command-extension             | Transport      | 003  | 04     | task-015                     | jcarloshg |
| task-017 | var-and-cvar-computation                   | Domain         | 004  | 05     | task-014                     | jcarloshg |
| task-018 | max-drawdown-distribution                  | Domain         | 004  | 05     | task-014                     | jcarloshg |
| task-019 | risk-report-aggregate                      | Domain         | 004  | 05     | task-017, task-018           | jcarloshg |
| task-020 | run-simulation-extends-risk-metrics        | Application    | 004  | 05     | task-016, task-019           | jcarloshg |
| task-021 | chart-artifact-contract                    | Domain         | 005  | 06     | task-019                     | jcarloshg |
| task-022 | matplotlib-renderer-adapter                | Infrastructure | 005  | 06     | task-021                     | jcarloshg |
| task-023 | filesystem-output-writer                   | Infrastructure | 005  | 06     | task-001                     | jcarloshg |
| task-024 | run-simulation-extends-visualization       | Application    | 005  | 06     | task-020, task-022, task-023 | jcarloshg |
| task-025 | structlog-event-wiring                     | Observability  | 006  | 07     | task-024                     | jcarloshg |
| task-026 | determinism-and-idempotency-tests          | Defense        | 006  | 07     | task-024                     | jcarloshg |
| task-027 | benchmark-gate-nfr-1                       | Defense        | 006  | 07     | task-024                     | jcarloshg |
| task-028 | e2e-docker-smoke-golden-file               | Delivery       | 006  | 08     | task-025, task-026, task-027 | jcarloshg |

## Layer-Order Invariant Check

The Playbook §8 rule: **no Layer 3 task depends on a Layer 4 task.**

Verified:

- task-003 (Transport) depends on task-002 (Domain). ✅ Layer 3 after Layer 2.
- task-009 (Transport) depends on task-008 (Application). ✅ Layer 3 after Application.
- task-015 (Application) depends on task-014 (Domain) and task-012 (Infra). ✅ Application after Domain/Infra.
- task-016 (Transport) depends on task-015 (Application). ✅ Layer 3 after Application.
- task-020 (Application) depends on task-016 (Transport) and task-019 (Domain). ✅ Application after Domain; the Transport dep is the upstream `simulate` command stub.
- task-024 (Application) depends on task-020, task-022, task-023. ✅ Application after Domain + Infra.
- task-025..027 (Observability + Defense) depend on task-024 (Application). ✅ Defense/Observability after the surface exists.
- task-028 (Delivery) depends on task-025..027. ✅ Delivery after Defense/Observability.

**No Layer-3-after-Layer-4 violation found.**

## Critical-Path Notes

- The critical path is: **task-001 → task-002 → task-005 → task-006 → task-007 → task-008 → task-009 → task-015 → task-016 → task-020 → task-024 → task-028** (Tracer Bullet → Portfolio → first orchestrator extension → Risk Metrics extension → Visualization extension → E2E smoke).
- Tasks task-010..014 (Market Data + Simulation core) can be developed in parallel with task-005..009 (Portfolio) since they only share the `task-004` (CI) dependency at the top.
- Tasks task-017..019 (RiskMetrics domain) only need task-014 (SimulationRun aggregate) and can run in parallel with task-015..016 (orchestrator extension for Portfolio+Sim) once those are unblocked.
- Single-developer note: parallel opportunities above are theoretical for this initiative (1 dev); they become real only if a second developer joins.

## Anti-Orphan Check

Every task has:
- ✅ A `Depends on:` field pointing to earlier task IDs only.
- ✅ An Epic parent (column 4).
- ✅ A named owner (column 7).
- ✅ A sprint assignment (column 5).

No orphaned tickets.
