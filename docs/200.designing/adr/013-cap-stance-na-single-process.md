# ADR-013 — CAP Stance — N/A; Single-Process Invariant

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Supersedes:** none
- **Source inputs:** `docs/00.defining.md` §200-Q3.x (consistency &
  failure tolerances), `docs/200.designing/02.designing.md` §2.3.2

## Context

The Designing playbook (§2.3) requires the CAP trade-off to be made
explicit: "On `us-east-1` lag, accept the order (Availability) or reject
it (Consistency). Document the choice in an ADR."

The CAP theorem applies to **distributed systems** that can suffer
**network partitions**. Our system:

- Is **single-process** (one Python process per run).
- Has **no network** (Defining Q5.5: no real third-party integrations).
- Cannot experience a partition because there is nothing to partition
  from itself.

Therefore the P leg of CAP does not occur. The A and C legs reduce to
**local properties**, not distributed-systems ones. We need to document
this so a future contributor doesn't waste time on "CAP trade-offs" that
don't apply, AND so a future production fork can identify the moment the
trade-off becomes real.

## Options Considered

1. **Pretend CAP applies; pick AP or CP anyway.** Document a "choice" of
   AP or CP for a system that has no P. Confusing and dishonest.
2. **Document that CAP does not apply; specify the equivalent local
   invariant.** Be explicit that the "consistency" we care about is
   intra-process atomicity of a `SimulationRun`.
3. **Defer the ADR; revisit when/if a network boundary is added.**
   Document the trigger condition.

## Decision

**Option 2 + Option 3.** This ADR documents both:

- **(a) CAP does not apply to v1.** The local equivalent of "consistency"
  is enforced: a `SimulationRun` is atomic (all-or-nothing).
- **(b) The trigger condition** that would make CAP apply is documented
  so the future fork knows when to revisit.

## Local "consistency" invariant (the CAP-N/A substitute)

A `SimulationRun` is **atomic**: it ends in exactly one of two terminal
states.

| Terminal state | Preconditions | Observable artifact |
|---|---|---|
| `COMPLETED` | All batches processed, `riskMetrics` set, no NaN/Inf, all events flushed. | `SimulationCompleted` event in `events.jsonl`; `status.json.status == COMPLETED`; `metrics.json` written. |
| `FAILED` | Any `DomainError` subclass raised mid-run. | `SimulationFailed` event in `events.jsonl`; `status.json.status == FAILED`; `failureReasonCode` set. |

The forbidden transitions in
`docs/100.planning/diagrams/state-machine-simulation-run.md` make the
invariant explicit:

- `PENDING → COMPLETED` is forbidden (must traverse `RUNNING`).
- `RUNNING → COMPLETED` requires all preconditions above.
- `RUNNING → FAILED` requires the `SimulationFailed` event to be flushed
  before the process exits.

**Enforcement:** the per-batch `flush()` (ADR-009) + the single-writer
thread model. There is no point at which the on-disk state can be
"halfway between COMPLETED and FAILED."

## CAP trigger condition (future)

CAP becomes a real question when:

1. A `MarketData` context is extracted AND calls a remote vendor, OR
2. A `Reporting` context is extracted AND reads from `RiskSimulation`'s
   store via the network, OR
3. Multi-user concurrency is added (Defining Q2.1 currently says DAU = 1).

When any of these becomes true, the CAP trade-off is a real negotiation
with the author (the "business" in this single-user context):

| Scenario | Likely choice | Rationale |
|---|---|---|
| Vendor returns 503 mid-run | **AP** — accept the run with stale returns, log a warning, persist `ReturnsLoaded` with `stale: true`. | Reproducibility is lost either way; losing a 30-second run is worse than using 5-minute-old returns. |
| Concurrent runs conflict on the same `portfolioId` | **CP** — reject the second run with `ResourceBusyError`. | Reproducibility requires that two simultaneous runs not share a portfolio snapshot. |
| `Reporting` reads from a stale `events.jsonl` | **AP** — show stale data; surface a `lastSyncedAt` indicator. | Reports are advisory; the source of truth is still `events.jsonl`. |

## Consequences

**Positive**
- No CAP negotiation is needed in v1.
- The local atomicity invariant is explicit and testable.
- The future trigger condition is documented so the next person doesn't
  have to re-derive it.

**Negative**
- None in v1.

**Reversibility**
- Fully reversible. When a network boundary is added, this ADR is
  superseded by one that documents the real CAP choice.