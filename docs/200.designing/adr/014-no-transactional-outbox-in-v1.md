# ADR-014 — No Transactional Outbox in v1; Single-Writer + Per-Batch Flush are Sufficient

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Supersedes:** none
- **Source inputs:** ADR-003 (file-based JSONL store), ADR-009 (batched
  events), `docs/200.designing/02.designing.md` §2.3.4

## Context

The Designing playbook (§2.3) calls out the **transactional outbox
pattern** as mandatory for any cross-system write:

> "Saving to DB then publishing to a broker sequentially is a lie — one
> will fail and the other won't know. Use the transactional outbox from
> day one for any cross-system write."

Our system has **no DB and no broker**. The "cross-system write" the
outbox pattern protects against does not exist. We need to document:

1. Why the outbox pattern is unnecessary in v1.
2. What equivalent guarantee we achieve instead.
3. The migration plan for the day a broker IS introduced.

## Options Considered

1. **Implement the outbox pattern anyway.** Add a `PendingEvent` table
   (SQLite) + a background worker. Belt-and-braces for a system with no
   remote broker.
2. **Skip the outbox; rely on single-writer sequential writes +
   per-batch flush.** Match the actual workload.
3. **Skip the outbox; rely on the OS filesystem's atomic write
   primitives (`rename(2)`).** Stronger guarantee than option 2 but
   adds platform-specific code.

## Decision

**Option 2.** The equivalent guarantee is achieved by three properties
that compose to "no half-written state":

1. **Single writer.** The engine is the only process that writes to
   `events.jsonl`. There is no concurrent producer.
2. **Single-threaded engine.** No `asyncio` task, no thread pool, no
   worker process. One Python thread owns the writer.
3. **Per-batch `flush()`.** Every 1,000-path batch ends with
   `JsonlEventWriter.flush()`, which calls `os.fsync()` on the file
   handle. The next batch cannot start until the prior batch is on disk.

The result is that the on-disk state is always at a batch boundary:

```
events.jsonl on disk:
  [SimulationRequested]
  [ReturnsLoaded]
  [PathSampled, batch=0]
  [DrawdownComputed, batch=0]
  [PathSampled, batch=1]
  [DrawdownComputed, batch=1]
  ...
  [PathSampled, batch=N-1]
  [DrawdownComputed, batch=N-1]
  [RiskMetricsCalculated]
  [SimulationCompleted]   ← terminal
```

A crash mid-batch loses at most one batch (~1 second of compute on the
NFR laptop baseline). The `status.json` file makes the partial state
visible: if `status.json.status == RUNNING` but `events.jsonl` is
truncated, the run is known to be corrupt and `ReplaySimulation` refuses
to touch it.

## What the outbox would protect against (and why we don't need it)

| Outbox risk | Do we have it? |
|---|---|
| DB write succeeds, broker publish fails → event lost | **No** — we have no DB and no broker. |
| Broker publish succeeds, DB write fails → event published without DB state | **No** — same reason. |
| Crash between two operations → inconsistent state | **No** — single thread, no two operations to interleave. |
| Concurrent writers interleave | **No** — single process. |
| Two-phase commit needed | **No** — single resource (the file). |

## Migration plan for the day a broker IS introduced

The day a Kafka adapter is added (e.g., for a future `MarketData`
context), the outbox pattern becomes necessary. The migration is:

```
TODAY (no outbox):
  engine.compute_batch()  ──►  JsonlEventWriter.write_event()  ──►  flush()
                                              │
                                              └── (the only consumer is the next batch)

FUTURE (with outbox):
  engine.compute_batch()  ──►  JsonlEventWriter.write_event()
                              │
                              ├──► flush() to JSONL (unchanged)
                              └──► append to outbox_table (new SQLite table)
                                       │
                                       └──► background worker
                                              │
                                              ├──► SELECT * FROM outbox_table WHERE published = FALSE
                                              ├──► publish to Kafka
                                              └──► UPDATE outbox_table SET published = TRUE
```

The outbox table is the **same** `SimulationResultStore` port with a new
adapter that writes to both JSONL and SQLite atomically. The background
worker is a new lightweight thread inside the engine process (not a
separate service — we still have one process per run).

## Consequences

**Positive**
- v1 ships with zero broker, zero outbox table, zero background worker.
- The migration plan is documented; the future work is bounded.

**Negative**
- A future broker addition is a non-trivial migration. We accept this
  because v1 does not need a broker (Defining Q4.1).

**Reversibility**
- Fully reversible. Adding the outbox is a new adapter behind
  `SimulationResultStore`; the domain is unchanged.