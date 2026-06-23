# ADR-001 — Single Bounded Context in v1 with Folder-Level Seams

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Source inputs:** `docs/00.defining.md` Q1.5, Q4.1, Q4.6

## Context

The project supports three logically distinct concerns: market data ingestion
(historical returns), risk simulation (Monte Carlo engine), and reporting
(metric aggregation + chart rendering). The defining doc explicitly anticipates
a future where a real third-party market-data vendor replaces the mock CSVs
(README note #3, defining doc Q4.6). We need to decide whether to model these
as three bounded contexts now, or to collapse them and preserve the seams as
folder structure only.

## Options Considered

1. **Three bounded contexts now.** Each context owns its own aggregates, ports,
   and adapters. A `Portfolio` in `RiskSimulation` and a `Portfolio` in
   `Reporting` would be separate types, requiring translation between them.
2. **Single bounded context `RiskSimulation` in v1.** Sub-folders exist for
   `market_data/` and `reporting/` to make the future seams visible, but no
   code is split into separate contexts yet. Folder-level seams keep the
   Anti-Corruption Layer (ACL) boundary locations explicit.
3. **No seams; flat structure.** Cheapest to build. Highest cost to extract
   later because every cross-cut is implicit.

## Decision

**Option 2.** We adopt a single bounded context `RiskSimulation` for v1. The
DDD layout under `src/domain/` will contain `portfolio/`, `simulation/`,
`market_data/` (empty), and `reporting/` (empty) as sub-folders, so the
ACL boundary is enforced by the import-linter from day one (see ADR-002).

## Consequences

**Positive**
- One aggregate (`SimulationRun`), one set of invariants — no risk of
  context-mapping bugs in a learning repo.
- All events share one envelope format; ordering is trivial (single writer).
- Folder seams make the future extraction cost a known, mechanical refactor
  (move files, introduce ACL adapters) rather than a redesign.

**Negative**
- A future vendor integration forces a context split, which is a non-trivial
  refactor. We accept this because the future is speculative and the
  alternative (premature split) doubles the surface area today.

**Reversibility**
- Reversible by extracting `market_data/` into a sibling package and
  introducing `MarketDataAcl` adapters in `src/infrastructure/market_data/`.
  No data shape changes (events are already versioned).
