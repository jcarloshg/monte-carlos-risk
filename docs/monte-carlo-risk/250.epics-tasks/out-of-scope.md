# Out-of-Scope Register — monte-carlo-risk (v1)

> Consolidated "not now" register across all 6 Epics. This file is the v2 backlog seed.
> Generated: 2026-06-23

Each item below was explicitly named as deferred in the originating Epic's §3. Items are grouped by Epic. Items that recur across multiple Epics are listed once with all sources noted.

---

## Deferred from Epic 001 — Tracer Bullet

- **Real-market-data adapter (HttpMarketDataSource).** Tracer Bullet ships `MockMarketDataSource` only; the HTTP adapter is a v2 stub raising `NotImplementedError`. Unblocked when Spike S-001 (vendor selection) completes.
- **HTTP service surface (FastAPI).** Tracer Bullet ships CLI only; an HTTP API is gated behind ADR-005 (CLI-only v1, defer HTTP).
- **Cloud deployment.** No remote infrastructure; runs locally in Docker per NFR-8 ($0/mo budget).

## Deferred from Epic 002 — Portfolio

- **Persistent portfolio storage.** Portfolios are YAML files or inline CLI specs. A portfolio DB / library is deferred to v2 (would supersede ADR-004 / ADR-009).
- **Portfolio rebalancing / re-weighting.** The v1 `Portfolio` is immutable once parsed; an `update_holdings()` or `rebalance()` operation is v2 work.
- **Multi-currency portfolios.** v1 assumes a single base currency per portfolio (the default).
- **Short positions / leverage / margin.** v1 disallows negative weights (invariant enforced in `task-006`); leveraged/inverse ETFs and short-selling are v2 work.

## Deferred from Epic 003 — Simulation + Market Data

- **Real market-data vendor integration.** Deferred to v2; gated by Spike S-001.
- **Antithetic variates / control variates / importance sampling.** v1 uses plain Monte Carlo with `SeedSequence` spawning per-path. Variance-reduction techniques are v2 work.
- **Multi-threaded / multi-process path generation.** v1 is single-threaded; numpy BLAS internal parallelism is allowed. True parallel Monte Carlo is v2 work.
- **Path-dependent derivatives / options.** v1 simulates terminal-wealth distributions only. American / Asian / barrier options are v2 work.

## Deferred from Epic 004 — RiskMetrics

- **Parametric VaR / Cornish-Fisher VaR.** v1 computes empirical (historical) VaR/CVaR only.
- **Expected Shortfall decomposition by factor.** v1 reports aggregate CVaR only; factor-attribution is v2 work.
- **Stress scenarios.** v1 reports the historical-simulation distribution only. Replay against 2008 / COVID / 2022 stress scenarios is v2 work.
- **Live monitoring / alerting.** v1 is a one-shot CLI. Real-time VaR/CVaR dashboards are v2 work.

## Deferred from Epic 005 — Visualization

- **Interactive charts (Plotly, Bokeh, Streamlit).** v1 ships static PNG via matplotlib. Interactive visualizations are v2 work.
- **Themed chart styles.** v1 uses a single pinned matplotlib `rcParams` set for determinism; alternative styles are v2 work (and would need to preserve determinism).
- **PDF / SVG export.** v1 emits PNG only. Other formats are v2 work.

## Deferred from Epic 006 — Run Pipeline / Quality

- **Production deployment / canary / feature flags.** Single-process educational CLI; no production rollout surface. Deferred to v2 if a hosted service is added.
- **Shift-right synthetic monitoring.** No production environment to monitor; deferred to v2.
- **Multi-region / active-active deployment.** N/A — single-machine.
- **Cross-platform byte-identical reproducibility.** Asserted **per-platform** (CI Linux image). macOS / Windows best-effort. Cross-platform determinism is v2 work and may require pinning BLAS.

## Cross-cutting deferred items (recurring)

- **Web UI / dashboard.** Explicitly rejected by ADR-005 (CLI-only v1). Becomes a candidate v2 Epic if/when the CLI alone is insufficient.
- **Persistent run history / database.** Explicitly rejected by ADR-004 / ADR-009 (zero datastores). Becomes a candidate v2 Epic if cross-run comparison is requested.
- **Message broker / event bus / Kafka.** Explicitly rejected by ADR-011 (no transactional outbox — no broker). Becomes a candidate v2 Epic if multi-process decomposition happens.
- **CQRS / read-side projections.** Explicitly rejected by ADR-008. Becomes a candidate v2 Epic if a dashboard query workload emerges.
- **Microservices decomposition.** Explicitly rejected by ADR-006 (modular monolith). Becomes a candidate v2 Epic if NFR-1 is violated on a single core or a second team joins.

## v2 Epic Candidates (consolidated from above)

When v2 planning begins, the following Epics are pre-scoped here:

1. **v2-Epic-A: Market Data Adapter** — Spike S-001 completion + HttpMarketDataSource implementation + rate-limit handling + cache layer.
2. **v2-Epic-B: Persistence Layer** — SQLite/DuckDB-backed run history; cross-run comparison UI (CLI or web).
3. **v2-Epic-C: Interactive Web UI** — FastAPI + lightweight frontend; removes CLI-only constraint (would supersede ADR-005).
4. **v2-Epic-D: Variance Reduction** — antithetic variates, control variates, importance sampling.
5. **v2-Epic-E: Real-Time Risk Dashboard** — shifts the tool from one-shot CLI to ongoing monitoring (would supersede ADR-006, ADR-011, possibly ADR-008).

These are **candidates**, not commitments. Each requires re-running the `000.defining` skill before any v2 work begins.
