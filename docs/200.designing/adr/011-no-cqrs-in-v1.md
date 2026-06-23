# ADR-011 — No CQRS in v1 (No Read/Write Split; Trigger for Future Adoption)

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Supersedes:** none
- **Source inputs:** `docs/00.defining.md` Q2.3 (read/write ratio N/A),
  `docs/00.defining.md` §200-Q1.7 (no read API), `docs/200.designing/02.designing.md` §2.2.2

## Context

The Designing playbook (§2.2) calls out CQRS as a pattern to consider
when "reads outnumber writes 100:1 or you need complex search views."
Our system has neither:

- **No read API.** The only "read" is opening a PNG, which bypasses the
  engine entirely (Defining Q2.3).
- **No read/write asymmetry.** A simulation writes one `metrics.json` and
  zero reads happen against the engine at runtime. The author's "read" is
  filesystem-bound and offline.
- **No complex search views.** There is no UI to search, no aggregation
  across runs, no dashboard.

We need to decide whether to introduce a write-side / read-side split
anyway (preparing for future search), or to defer until a real trigger
exists.

## Options Considered

1. **CQRS from day one.** Write-side writes to a normalized store; a
   projector populates a denormalized read-store (Redis / DuckDB / SQLite).
   All query paths read from the read-store.
2. **No CQRS in v1; defer until a query surface exists.** The
   `SimulationResultStore` is the only persistence interface. A future
   `Reporting` context with a query endpoint is the natural CQRS adoption
   point.
3. **CQRS-lite: per-run `index.jsonl` for fast `ls`-style queries.** No
   separate store; just a precomputed index file.

## Decision

**Option 2.** v1 has no read API. The `SimulationResultStore` port
(ADR-003, ADR-014) is the single persistence interface for both writes
(events) and the future reads. The future adoption trigger is documented
below.

## Future adoption trigger

If and only if **all three** of these become true, adopt CQRS:

1. A `Reporting` context is extracted (per ADR-001) AND
2. The `Reporting` context needs to query across runs (not just one run at
   a time) AND
3. The latency budget for cross-run queries is below what a one-shot
   `cat events.jsonl | jq` can deliver (sub-second).

When triggered, the adoption is:

```
SimulationResultStore (write-side)
    └── writes events.jsonl per run (unchanged)

ReportingReadStore (new port)
    └── projector consumes events.jsonl from all runs
    └── persists to a denormalized store (DuckDB is the natural choice:
        in-process, single-file, fast analytical queries)

ReportingUseCase
    └── reads from ReportingReadStore (NEVER from SimulationResultStore)
```

The projector pattern keeps the write-side pure and the read-side
denormalized — the canonical CQRS shape.

## Consequences

**Positive**
- v1 ships with one store, one writer, zero read complexity.
- The `SimulationResultStore` port is exactly the right shape to absorb
  a future CQRS adoption without touching the domain.

**Negative**
- A future `Reporting` context forces a context split + CQRS adoption,
  which is a non-trivial refactor. We accept this because the future is
  speculative and the alternative (premature split) doubles the surface
  area today.

**Reversibility**
- Fully reversible by adding `ReportingReadStore` (new port) +
  `JsonlProjector` (adapter) + a `ReportingUseCase`. The
  `SimulationResultStore` and the domain are unchanged.