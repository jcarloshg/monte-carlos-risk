# ADR-008 — No CQRS

- **Status:** Accepted
- **Date:** 2026-06-23
- **Deciders:** jcarloshg
- **Source:** `00.defining.md` §1 Domain & Flow; `01.planning.md` §1 Bounded Contexts; Design playbook §Micro Architecture (*"CQRS for Asymmetric Loads"*).
- **Related:** ADR-009 (zero datastores).

## Context

The Design playbook lists CQRS as a candidate pattern: *"When reads outnumber writes 100:1 or you need complex search views, segregate: commands write to normalized SQL, emit events, and a projector populates a denormalized read store."*

The question for this project is whether any of the four bounded contexts exhibits read/write asymmetry or would benefit from a denormalized read view.

## Analysis per context

| Context | Writes per run | Reads per run | Asymmetry? | Complex search view? |
|---|---|---|---|---|
| **Portfolio** | 1 (parse YAML, validate) | 0 (used as input to Simulation) | No | No |
| **Simulation** | 1 (generate PathSet) | 0 (used as input to RiskMetrics) | No | No |
| **RiskMetrics** | 1 (compute RiskReport) | 1 (consumed by Visualization) | No | No |
| **Visualization** | 3 (3 PNGs) | 1 (consumed by user + report.json) | No | No |
| **Cross-run** | 0 (no persistence per ADR-004/ADR-009) | 0 (no read store) | N/A | N/A |

The read:write ratio across the entire pipeline is **1:1** (or less, since reads often happen synchronously immediately after writes within the same use case). There is no asymmetric load and no complex search view to project.

## Decision

**No CQRS.** No `commands/`, `queries/`, `projectors/`, or read-store directories. No denormalized read store. The orchestrator calls aggregates directly; aggregates return value objects that the next use case consumes.

## Consequences

**Positive.**
- No projector code, no read-store schema, no eventual-consistency window between write and read.
- Within a single run, the data flow is fully synchronous and locally deterministic (NFR-4).
- One less pattern for the single developer to maintain.

**Negative.**
- If a future v2 introduces an HTTP service with a dashboard that re-queries prior runs (a plausible v2 trigger), a read-side projection may become useful. At that point, this ADR must be re-opened and CQRS adopted selectively — most likely for the dashboard projection only, not for the simulation pipeline itself.

**Supersedes.** None.

**Migration trigger.** A future ADR should re-evaluate this decision if:
- A persistent read store is added (would supersede ADR-009), AND
- A query workload emerges that scans across many runs (e.g., "show me the VaR distribution across my last 100 simulations").
Until both conditions hold, CQRS is rejected as gold-plating.
