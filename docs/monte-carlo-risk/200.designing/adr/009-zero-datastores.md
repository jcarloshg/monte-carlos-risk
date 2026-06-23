# ADR-009 — Zero Datastores (Polyglot Persistence Rejected)

- **Status:** Accepted
- **Date:** 2026-06-23
- **Deciders:** jcarloshg
- **Source:** `00.defining.md` §2 Data Strategy (no persistence); Planning ADR-004; NFR-8 ($0/mo cloud).
- **Related:** ADR-008 (no CQRS — both follow from "no persistent store"), `diagrams/db-erd.md`.

## Context

The Design playbook §Data Architecture says *"Polyglot Persistence. Pick the right tool per workload: PostgreSQL/Aurora for ACID, DynamoDB for massive-scale key-value, Redis for cache and rate-limiting. … Acknowledge CAP explicitly."*

The question is what (if any) datastores this project needs. Planning ADR-004 ruled out persistence in v1; this Design ADR formalizes the "polyglot persistence" question on those grounds.

## Workload analysis

| Workload | Need a DB? | Why / Why not |
|---|---|---|
| User identity / auth | No | Single-user, no login. CLI runs are anonymous. |
| Portfolio storage | No | Portfolio is a CLI flag or a file path. The user owns their portfolio YAML. |
| Market data cache | No | The bundled mock corpus IS the cache. A real-API v2 might add a small on-disk cache — see below. |
| Simulation results history | No | ADR-004 forbids it; NFR-4 (reproducibility) is satisfied from CLI inputs alone. |
| Run metadata for observability | No | structlog writes to stderr; nothing is shipped to a TSDB, log aggregator, or APM tool (no cloud spend). |
| Distributed state across processes | No | ADR-006 — one process. |
| Read-side projections for queries | No | ADR-008 — no CQRS. |

## Options

1. **PostgreSQL** for everything (overkill). Adds: managed Postgres (cost > $0), schema migrations, ORM or `psycopg`, backup story. Rejected.
2. **SQLite** as a single-file embedded DB. Adds: schema, migrations, locking semantics. Rejected — provides no value over `--output-dir` JSON files for v1.
3. **DuckDB** for analytical queries on simulation results. Tempting but: no queries are run across runs in v1; the JSON report is the analysis output. Rejected.
4. **Redis** as a cache. Rejected — there is no upstream service to cache.
5. **No datastore at all.** The "database" is the filesystem (read-only bundled CSV corpus + write-only `--output-dir` JSON/PNG).

## Decision

**Option 5: zero datastores.**

There is no SQL DB, no document store, no cache, no queue, no Parquet files, no `data/*.db`. The bundled mock corpus lives in `data/mock/*.csv` (versioned in git, read-only at runtime). Per-run artifacts live in `--output-dir` (configurable; default `./output`; not gitignored).

Reproducibility (NFR-4) is derived from `(seed, portfolio, n_paths, horizon, mock_data_version)` alone — none of these need a database to be reproducible.

## Consequences

**Positive.**
- Zero persistence-layer complexity: no migrations, no schema evolution, no backup story.
- $0/mo cloud budget (NFR-8) is structurally enforced — no managed Postgres, no managed Redis.
- `diagrams/db-erd.md` is intentionally empty (the "NOTHING" entity). Future contributors cannot accidentally grow a god database.
- The `.importlinter` contract explicitly forbids `sqlalchemy`, `django`, `peewee`, `tortoise`, `piccolo`, `prisma`. Drift is caught in CI.

**Negative.**
- No historical comparison across runs without manual file management. Mitigated by the deterministic artifact filenames (`{run_id}_report.json`) and the self-describing JSON report.
- A future "compare my last N runs" feature requires this ADR to be superseded.

**Anti-patterns rejected.**
- **Database-Driven Design** — no ORM, no schema, no migrations.
- **God Database** — by construction, no DB exists for multiple services to share.
- **Gold-Plating Scalability** — no sharding, no replicas, no multi-AZ.

**Supersedes.** None (restates Planning ADR-004 at the Design-phase "polyglot persistence" level).

**Migration trigger.** A future ADR should re-evaluate this decision if:
- A second developer joins and wants shared state across machines.
- A v2 HTTP service (would supersede ADR-005) needs persistent state.
- The bundled mock corpus grows beyond what fits in git (currently ~MB; if it grows to GB, an external Parquet-on-S3 store becomes justified).

When triggered, a minimal schema is sketched in `diagrams/db-erd.md` §"What the DB ERD would look like in v2" — but it is NOT committed code.
