# ADR-003 — File-Based JSONL Event Store (No Database, No Broker)

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Source inputs:** `docs/00.defining.md` Q3.1, Q3.4, 200-Q4.x, README note #1

## Context

The system produces 7 event types per simulation run (Defining Q1.4). A
realistic quant shop would publish these to Kafka with an outbox table and
DLQ. For v1 we need to choose how the in-process event log is persisted.

## Options Considered

1. **Kafka + outbox.** Production-grade. Requires a Docker Compose service,
   topic provisioning, schema registry integration. Overkill for a single
   notebook-equivalent learning project.
2. **SQLite.** Lightweight, file-based, supports transactional writes. Adds a
   dependency (`sqlite3` stdlib is fine, but schema migrations become a real
   concern).
3. **JSONL append-only log per run.** One file at
   `./output/<runId>/events.jsonl`. Stdlib only. Sequence numbers and
   per-run ordering are trivial. No migrations ever.

## Decision

**Option 3.** Each run writes its events to `./output/<runId>/events.jsonl`
with one JSON object per line. The envelope is:

```json
{
  "schemaVersion": "1.0.0",
  "runId": "uuid",
  "sequenceNumber": 7,
  "correlationId": "uuid",
  "occurredAt": "2026-06-22T12:34:56.789Z",
  "eventType": "SimulationCompleted",
  "payload": { ... }
}
```

The writer is `SimulationResultStore` (port) implemented by
`JsonlEventWriter` (adapter) in `src/infrastructure/persistence/`. Writes are
flushed per batch of 1,000 paths (matches ADR-009 granularity) so a crash
mid-run loses at most one batch.

## Consequences

**Positive**
- Stdlib only (`json`, `pathlib`). Zero infra cost.
- `cat events.jsonl | jq` works for ad-hoc inspection.
- Future migration to Kafka is mechanical: replace the adapter, replay the
  existing JSONL files into the topic on first publish.

**Negative**
- No cross-run queries without an out-of-band index. We accept this — the
  CLI smoke test and `ls ./output/` are the only consumers.
- No atomic multi-event transactions. Mitigated by the single writer (the
  engine thread); events are causal and partial states are recoverable by
  reading the final `status.json`.

**Reversibility**
- Reversible by introducing a Kafka adapter behind the same port. JSONL
  becomes the seed for a one-time replay.
