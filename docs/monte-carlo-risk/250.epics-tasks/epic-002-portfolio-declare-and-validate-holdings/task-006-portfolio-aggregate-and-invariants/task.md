# Task 006 — Portfolio Aggregate + Invariants

**Epic:** epic-002-portfolio-declare-and-validate-holdings
**Layer:** Domain
**Sprint:** 02
**Depends on:** task-005
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 300 LOC

## Context

The first Domain aggregate. Encodes the four invariants from `00.defining.md` §2 Bounded Contexts: weights sum to 1.0 (within 1e-9), no duplicate tickers, non-empty holdings, no negative weights. Traces to Stories 2.1, 2.2.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given three `Holding`s `(AAPL, 0.4)`, `(MSFT, 0.3)`, `(GOOG, 0.3)`, When I construct `Portfolio(holdings=...)`, Then the aggregate exists, exposes `.holdings` as a tuple, and `.tickers` as a tuple of `Ticker`s.
- [ ] **Scenario 2 (Sad Path):** Given holdings summing to 0.95, When I construct `Portfolio`, Then `WeightsSumMustEqualOne` (a typed exception) is raised. Same for duplicates, empty list, or negative weight.
- [ ] **Edge Case (Mandatory):** If holdings sum to 1.0 + 1e-10 (within the 1e-9 tolerance), the aggregate is constructed successfully. If they sum to 1.0 + 1e-8 (outside the tolerance), `WeightsSumMustEqualOne` is raised. The edge case is asserted by a parameterized unit test with at least three values inside and three outside the tolerance.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** N/A.

## Out of Scope

- YAML / inline parsing factories (`task-007`).
- The `PortfolioDefined` event class itself (event lives in `domain/portfolio/events.py` and is emitted by `task-008`).

## Deliverables

- `src/monte_carlo_risk/domain/portfolio/portfolio.py` — `@dataclass(frozen=True, slots=True) class Portfolio(holdings: tuple[Holding, ...])` with `__post_init__` enforcing invariants.
- `src/monte_carlo_risk/domain/portfolio/invariants.py` — pure functions: `weights_sum_to_one(holdings) -> bool`, `no_duplicates(holdings) -> bool`, `weights_non_negative(holdings) -> bool`, with a constant `WEIGHT_SUM_TOLERANCE = 1e-9`.
- Typed exceptions in `src/monte_carlo_risk/domain/portfolio/exceptions.py`: `WeightsSumMustEqualOne`, `DuplicateTicker`, `EmptyHoldings`, `NegativeWeight` — each carrying a context dict for the CLI error envelope.
- `tests/unit/domain/portfolio/test_portfolio.py` — happy + sad + tolerance-edge cases.
- `tests/unit/domain/portfolio/test_invariants.py` — pure-function tests for each invariant.
