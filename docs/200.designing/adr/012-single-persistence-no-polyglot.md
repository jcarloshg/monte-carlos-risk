# ADR-012 — Single Persistence Choice (No Polyglot; stdlib JSONL is Sufficient)

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Supersedes:** none
- **Source inputs:** `docs/00.defining.md` §200-Q4 (workload characteristics),
  ADR-003 (file-based JSONL store), `docs/200.designing/02.designing.md` §2.3.1

## Context

The Designing playbook (§2.3) calls for **polyglot persistence** —
"pick the right tool per workload: PostgreSQL/Aurora for ACID transactions,
DynamoDB for massive-scale key-value, Redis for ephemeral cache and
rate-limiting."

Our workload has:

| Property | Value |
|---|---|
| Writers | 1 (the CLI process) |
| Readers | 1 (the CLI smoke test) |
| Concurrency | 0 (Defining Q2.2 — DAU = 1) |
| Data volume | < 1 MB per run (Defining Q2.4) |
| Query patterns | None (no read API, Defining Q2.3) |
| Transactions | None (single writer; atomicity is file-level) |

The polyglot decision matrix collapses to one column: there is only one
workload characteristic that matters (single writer, single reader, no
queries) and one tool satisfies it (stdlib JSONL). We need to document
this explicitly so a future contributor doesn't add Postgres "just in
case."

## Options Considered

1. **Polyglot from day one.** PostgreSQL for events + Redis for "hot
   reads" + S3 for archival. Production-shaped. Requires Docker Compose
   services, schema migrations, and an ORM. Massive overkill for the
   workload.
2. **Single persistence choice (stdlib JSONL).** `pathlib` + `json` +
   per-batch `flush()`. Zero infra cost. Matches the workload exactly.
3. **SQLite as a middle ground.** Single file, supports SQL, supports
   transactions. Adds a dependency and a schema migration story for
   marginal benefit.

## Decision

**Option 2.** The system uses **one persistence surface**:
`./output/<runId>/`, consisting of:

- `status.json` (terminal state)
- `events.jsonl` (append-only event log, ADR-003)
- `metrics.json` (final risk metrics)
- `*.png` (rendered charts)

All four are stdlib-only. No ORM, no SQL, no migrations.

## Workload → tool match (frozen table)

| Workload characteristic | Tool chosen | Justification |
|---|---|---|
| Append-only event log | `jsonl` (stdlib) | O(1) append, `cat | jq` works, no schema migration |
| Terminal state | `status.json` (stdlib) | One file, written 1-3 times per run |
| Final metrics | `metrics.json` (stdlib) | One file, written once at terminal transition |
| Rendered charts | `*.png` (matplotlib → filesystem) | Matplotlib's native output |
| ACID transactions | **N/A** | Single writer, no concurrency |
| Cross-run queries | **N/A** | No read API (ADR-011) |
| Cache / rate-limiting | **N/A** | No read API, no inbound traffic |
| Archival / cold storage | **N/A** | Outputs persist on the author's laptop |

## Future trigger for polyglot adoption

If and only if **any** of these becomes true, re-evaluate:

1. A `Reporting` context is extracted AND needs cross-run queries →
   add **DuckDB** as the read-store (ADR-011).
2. Real-time concurrent runs from multiple users → add **PostgreSQL**
   with row-level locking on `SimulationRun.status`.
3. Massive horizontal scale (> 10k runs/day) → add **Kafka** as the
   event broker + **S3** for archival.

Until then, "premature polyglot" is rejected as anti-pattern #5 in
`docs/200.designing/02.designing.md` §3.

## Consequences

**Positive**
- Zero infra cost ($0/month budget, Defining Q2.5).
- Stdlib only — no version-drift, no CVE pipeline, no migration tooling.
- The `SimulationResultStore` port is exactly the right shape to absorb
  a future polyglot adoption.

**Negative**
- No cross-run queries. Acceptable — no read API exists (Defining Q2.3).
- No ACID transactions across files. Acceptable — single writer.

**Reversibility**
- Fully reversible. Adding a database is a new adapter behind
  `SimulationResultStore`; the domain is unchanged.