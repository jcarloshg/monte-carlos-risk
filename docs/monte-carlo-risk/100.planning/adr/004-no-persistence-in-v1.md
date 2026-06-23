# ADR-004 — No Persistence Layer in v1

- **Status:** Accepted
- **Date:** 2026-06-23
- **Deciders:** jcarloshg
- **Source:** `00.defining.md` §2 Data Strategy; `01.planning.md` §2 NFR-4, NFR-5.

## Context

The defining phase confirmed: "No persistence — pure in-memory per run." (`00.defining.md` §2 Data Strategy). Each CLI run loads mock data, runs the simulation, emits PNG + JSON to a configurable output directory, and exits. Nothing is retained across runs.

Some adjacent projects in this space (notebook-driven quant research) default to persisting run results in SQLite or DuckDB for later comparison. The defining phase explicitly rejected this for v1.

## Options

1. **SQLite database.** Persist `runs`, `parameters`, `metrics` tables. Queryable history. Adds a dependency and a migration story.
2. **Append-only `results/` directory.** Save each run's PNG + JSON under a timestamped folder. No DB, no migrations, human-grepable.
3. **No persistence.** Output artifacts go only to a user-configurable `--output-dir` (default `./output`). The directory is overwritten on each run with the same seed. Nothing is retained unless the user copies it out.

## Decision

**Option 3: no persistence layer.**

- The CLI accepts `--output-dir` (default `./output`). Each run writes `{run_id}_paths.png`, `{run_id}_drawdown.png`, `{run_id}_fan_chart.png`, and `{run_id}_report.json` to that directory.
- A second run with the **same `--seed` and same inputs** overwrites the previous artifacts byte-identically (NFR-5: idempotency).
- The directory is **not** gitignored by the project (the user may or may not want it — their choice).
- No SQLite, no DuckDB, no Parquet, no ORM. The "database" is the filesystem.

## Consequences

**Positive.**
- Zero persistence-layer complexity: no migrations, no schema evolution, no backup strategy.
- Reproducibility comes from `(seed, portfolio, n_paths, horizon, mock_data_version)` — all inputs are CLI flags or config files. NFR-4 is satisfied without a database.
- Honors the project goal (educational, single-developer, single-machine).

**Negative.**
- No historical comparison across runs without manual file management. Mitigated by the deterministic artifact naming and the JSON report being a self-describing snapshot.
- If v2 wants "compare my last 10 runs" as a feature, a persistence layer must be added. That will require a new ADR and a new Spike.

**Supersedes.** None.
