# ADR-009 — Batched Event Granularity (PathSampled Emitted per 1,000 Paths)

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Source inputs:** `docs/00.defining.md` 200-Q1.4

## Context

A 10,000-path run would emit 10,000 `PathSampled` events if we followed
strict event-per-path. That's 10,000 JSONL writes plus 10,000 log lines —
most of which carry no information the human author needs at that
granularity. We need to fix the batching policy.

## Options Considered

1. **One event per path.** Maximally granular. Wastes I/O and log volume.
2. **One event per batch of 1,000 paths.** Matches the JSONL flush
   cadence (ADR-003). A 10k run emits 10 events; a 100k run emits 100.
3. **One `SimulationProgress` event with a `pathsCompleted` counter.**
   Smallest volume, but loses the per-batch idempotency boundary (a crash
   mid-batch would replay the whole run).

## Decision

**Option 2.** `PathSampled` and `DrawdownComputed` events are emitted
**once per 1,000-path batch**. The batch size is a constant
`BATCH_SIZE = 1000` defined in `src/domain/simulation/engine.py`. The
flush boundary is the same: the JSONL writer is `flush()`ed at the end
of each batch.

The `payload.pathIndexRange` field carries `[start, end)` (inclusive of
start, exclusive of end) so a downstream consumer can reconstruct the
exact paths without ambiguity. Tests assert that the sum of
`pathIndexRange` lengths across a run equals `NumberOfPaths`.

## Consequences

**Positive**
- ~10 events for a typical run instead of 10,000. Human-readable log
  output, smaller JSONL files.
- Each batch is one JSONL flush, so a crash loses at most one batch
  (~1 second of compute on the NFR laptop baseline).
- Batch boundary is the natural unit for idempotent retries (future Kafka
  consumer can dedupe by `sequenceNumber`).

**Negative**
- Downstream consumers wanting per-path events must reconstruct from
  the batched event + the persisted seed. The defining doc already
  acknowledges this trade-off (200-Q1.4).

**Reversibility**
- Reversible by lowering `BATCH_SIZE` to 1 (constant change).
