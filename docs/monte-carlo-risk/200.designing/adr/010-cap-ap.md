# ADR-010 — CAP Trade-Off: AP for All Four Contexts

- **Status:** Accepted
- **Date:** 2026-06-23
- **Deciders:** jcarloshg
- **Source:** `00.defining.md` §1 Resilience & Compliance; Planning ADR-001 §Consequences; NFR-4 (reproducibility), NFR-5 (idempotency).
- **Related:** ADR-006 (modular monolith), ADR-009 (zero datastores), ADR-011 (no transactional outbox).

## Context

The Design playbook §Data Architecture says *"Acknowledge CAP explicitly. Partitions will happen. Negotiate with the business: on `us-east-1` lag, accept the order (AP, risk overselling) or reject it (CP, lose the sale). Document the choice in an ADR."*

For a distributed system, CAP poses a real choice: under a network partition, do you serve potentially-stale data (AP) or refuse to serve (CP)? The business's answer determines the entire data-layer topology.

This project is **not** distributed in v1. There is no network partition to negotiate. However, the playbook requires the choice to be documented, because the answer binds future v2 work and is a place where bad defaults silently propagate.

## Per-context CAP stance

| Context | v1 Stance | Justification |
|---|---|---|
| **Portfolio** | **AP** (trivially) | Single-process in-memory state. No replication, no consensus, no partition. "Consistency" collapses to "the parsed YAML agrees with itself." |
| **Simulation** | **AP** (trivially) | Same. The RNG is deterministic given the seed (NFR-4); the path generator cannot return "stale" data because there is no other source of paths. |
| **RiskMetrics** | **AP** (trivially) | Pure function over a `PathSet`. No external dependency. |
| **Visualization** | **AP** (trivially) | Pure function over a `RiskReport` + `PathSet`. No external dependency. |

In all four contexts, **P** (network partition) cannot occur in v1 because there is no network — the only communication is in-process method calls within one Python process on one machine.

The stronger guarantee we actually provide is **local determinism** (NFR-4): the same inputs produce the same outputs, always. This is **strictly stronger** than CAP's "strong consistency" because there is no distributed state for replicas to disagree about.

## Decision

**AP stance documented for all four contexts.** The reasoning is: in v1 there is no partition to tolerate, so the CAP trade-off collapses to "always available (because there's only one node that could fail), always consistent (because there's only one node that could disagree with itself)." When a v2 introduces a real distributed store or message broker, this ADR must be re-opened and the trade-off re-negotiated with the business.

## What "AP" means in v1

- If the process crashes mid-run, the run is lost (the user re-runs). There is no "accept the order and reconcile later" because there is no order — there is only one CLI run.
- There is no "reject under partition" because there is no partition.
- There is no eventual-consistency window. Reads are always consistent with the just-completed write because the read happens in the same process.

## What "AP" would mean if v2 adds a distributed store

If a v2 introduces (say) a Postgres database and an event broker, the choice becomes real:

| Context | Recommended AP/CP stance for v2 | Reason |
|---|---|---|
| Portfolio | CP (if persisted) | A portfolio that's read as `sum != 1.0` after a `validate-portfolio` write is a bug; refuse to serve stale reads. |
| Simulation | AP | A slightly stale cached `PathSet` is fine; the user will re-run if results look wrong. |
| RiskMetrics | AP | Pure function; can be re-computed from cached `PathSet`. |
| Visualization | AP | Pure function; can be re-rendered from cached `RiskReport`. |

This table is **a starting point for v2 negotiation**, not a binding decision. The actual choice in v2 requires re-running this Design phase.

## Consequences

**Positive.**
- v1 has the strongest possible consistency guarantee — local determinism — without distributed-system cost.
- Future v2 contributors have a documented starting point for per-context CAP negotiation.

**Negative.**
- The CAP trade-off is a non-question in v1; this ADR may feel like over-documentation. Mitigated by the playbook requiring it and by the table above giving v2 a head start.

**Anti-patterns rejected.**
- **"Build It and They Will Come."** No Kafka, no Raft, no Paxos, no leader election — none are needed in v1.

**Supersedes.** None.

**Migration trigger.** A future ADR should re-open this decision when:
- A persistent store is added (would supersede ADR-009), OR
- A message broker is added (would supersede ADR-011), OR
- The process is split into multiple processes (would supersede ADR-006).
