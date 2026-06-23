# ADR-011 — No Transactional Outbox

- **Status:** Accepted
- **Date:** 2026-06-23
- **Deciders:** jcarloshg
- **Source:** Planning ADR-005 (CLI-only v1, no broker); Design playbook §Data Architecture (*"Transactional Outbox for reliable dual-writes"*); NFR-4, NFR-5.
- **Related:** ADR-006 (modular monolith), ADR-009 (zero datastores), ADR-010 (CAP).

## Context

The Design playbook says: *"Transactional Outbox for reliable dual-writes. Write entity + outbound event to two tables in the same Postgres transaction; a worker (or Debezium) polls the outbox and publishes to the broker. At-least-once delivery without distributed transactions."*

The pattern solves a specific problem: when a single business operation needs to (a) write to a database and (b) publish an event to a message broker, and those two actions cannot be made atomic without a distributed transaction.

The question for this project is whether the transactional-outbox pattern is needed.

## Analysis

The transactional-outbox pattern requires **all** of the following to be applicable:

1. A **persistent store** to which writes happen (the entity side of the dual-write). → ADR-009 says: zero datastores. **Not present.**
2. A **message broker** to which events are published (the event side of the dual-write). → ADR-005 / ADR-006 say: CLI-only, single process, no broker. **Not present.**
3. A **distributed topology** where the writer process and the broker could fail independently. → ADR-006 says: modular monolith. **Not present.**

All three prerequisites are absent in v1. Therefore the dual-write problem the outbox solves cannot occur.

What about the **in-process** event emission (the `SimulationStarted`, `SimulationCompleted`, etc. events in `events.schema.json`)? Those are **not** dual-writes — they are:

- A return value of the method that emitted them.
- Passed by reference within the same process.
- Synchronously consumed by the next step in the orchestrator.

There is no opportunity for a partial-write inconsistency. If the orchestrator raises an exception between emitting `SimulationStarted` and emitting `SimulationCompleted`, the `SimulationStarted` event is discarded along with the partial run; nothing is persisted; nothing needs to be reconciled.

## Decision

**No transactional outbox in v1.** No `outbox/` table, no `OutboxRelay` worker, no Debezium connector, no dual-write logic anywhere in the codebase.

## Consequences

**Positive.**
- One less moving part. The orchestrator's event emission is just `return event` / `yield event`, with no persistence concern.
- No "what if the outbox row was written but the broker publish failed" failure mode to handle.
- The CI test `events-schema-validation` (per `architecture/contract-deviations.md`) verifies the orchestrator emits exactly the events in the frozen order; no outbox would make this test harder.

**Negative.**
- None for v1. The pattern's only cost is its absence — if a dual-write situation arises, the cost of adding the pattern is bounded (the `outbox/` table, the relay worker, the schema migration).

**Anti-patterns rejected.**
- **Gold-Plating Scalability** — adding an outbox for a system with no broker and no DB.

**Supersedes.** None.

**Migration trigger.** A future ADR should re-open this decision when **both** of these become true:
- A persistent store is added (would supersede ADR-009), AND
- A message broker is added (would supersede ADR-005 / ADR-006's CLI-only / monolith stance).

When triggered, the outbox pattern should be adopted for any context whose business operation spans a write to the DB and an event publication. A first candidate would be `Portfolio` if portfolios become persistent and `PortfolioDefined` becomes a broker event consumed by downstream services.
