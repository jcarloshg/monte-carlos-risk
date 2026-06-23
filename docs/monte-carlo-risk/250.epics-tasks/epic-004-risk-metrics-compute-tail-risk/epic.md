# Epic 004: Risk Metrics — Compute Tail Risk and Drawdowns

**Status:** Ready
**Bounded Context:** RiskMetrics
**Sequence Order:** 4 of 6 (Value)
**Estimated Sprints:** 1

> Turns a `PathSet` into a `RiskReport` that quantifies tail risk and drawdown distribution. Pure domain math: no I/O, no matplotlib. The first Epic where the user gets actionable numbers (VaR, CVaR, max drawdown percentiles).

## 1. Business Context & Value

- **Why are we building this?** A `PathSet` is interesting but not actionable. Risk metrics let the user answer: *"What's my expected 1-day 95% VaR? What's my CVaR? What does my drawdown distribution look like?"* These are the headline numbers in any quant risk report.
- **Success Metrics:**
  - On a synthetic `PathSet` of 10,000 paths with `N(0.0005, 0.01)` daily log returns, the reported VaR(95%), CVaR(95%), and max-drawdown percentiles agree with closed-form expectations **within 5%** relative error (Monte Carlo sampling noise).
  - Adding the RiskMetrics step to the pipeline does not push the total run beyond NFR-1 (P50 ≤ 10 s, P95 ≤ 30 s) — leaving headroom for Visualization.

## 2. Architectural Scope (C4 Level 2)

- **Containers Touched:** `RiskReport` aggregate + `VaR`, `CVaR`, `DrawdownDistribution` value objects (`domain/risk_metrics/`); `RunSimulation` orchestrator extended (`application/use_cases/`).
- **External Dependencies:** numpy (whitelisted in `domain/` per ADR-002).
- **Database Impact:** None.

## 3. Strict "Out of Scope"

- **Parametric VaR** (assumed normal returns) — v1 uses historical-simulation (empirical) only.
- **Factor decomposition** of CVaR — v1 reports aggregate only.
- **Stress scenarios** (2008, COVID) — v2.
- **Live monitoring** — v1 is one-shot CLI.
- **Chart rendering of risk metrics** — Epic 005.

## 4. Non-Functional Requirements (NFRs)

- **NFR-1:** RiskMetrics computation adds **≤ 1 s** to a default run (asserted by benchmark in `task-027`).
- **NFR-4:** Risk metrics are deterministic given the input `PathSet` (no internal RNG). A re-run with the same seed produces the same `RiskReport`.
- **NFR-3:** `domain/risk_metrics/` has zero forbidden imports.

## 5. Required Technical Artifacts (Definition of Ready)

- [ ] C4 Container Diagram approved. ✅
- [ ] CLI contract section approved. ✅ `cli-contract.yaml` §`schemas.simulation_report.risk_report` is frozen.
- [ ] UI/UX designs approved. **N/A — CLI-only per ADR-005.**
- [ ] Event schemas merged. ✅ `RiskMetricsCalculated` payload (the full `RiskReport`) is frozen in `events.schema.json`.

## 6. User Stories (BDD)

- **Story 4.1:** Compute VaR and CVaR from a `PathSet`.
  - *Scenario:* `Given` a `PathSet` of 10,000 normal-return paths and `confidence = 0.95`, `When` `RiskReport.from_path_set(path_set, confidence)`, `Then` `var` is the 5th percentile of the terminal-wealth loss distribution and `cvar` is the mean loss conditional on loss exceeding `var`.
  - *Edge Case placeholder:* handled in `task-017`.
- **Story 4.2:** Compute max-drawdown distribution.
  - *Scenario:* `Given` a `PathSet`, `When` `RiskReport.from_path_set`, `Then` `max_drawdown_distribution.{mean, std, p05, p50, p95}` are present and consistent (e.g., `p05 ≤ p50 ≤ p95`).
  - *Edge Case placeholder:* handled in `task-018`.
- **Story 4.3:** End-to-end `simulate` includes the `risk_report` block.
  - *Scenario:* `Given` the RiskMetrics extension to `RunSimulation` is wired, `When` I run `monte-carlo simulate`, `Then` `simulation_report.json` has `risk_report` populated with all five required sub-objects.
  - *Edge Case placeholder:* handled in `task-020`.
