# Task 005 — Portfolio Shared-Kernel Extensions

**Epic:** epic-002-portfolio-declare-and-validate-holdings
**Layer:** Domain
**Sprint:** 02
**Depends on:** task-002
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 200 LOC

## Context

Adds the `Holding` value object used by the `Portfolio` aggregate. Holds (ticker, weight) pairs and is the building block for the aggregate root. Traces to Story 2.1.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a `Holding(Ticker("AAPL"), Weight(0.4))`, When I read `.ticker` and `.weight`, Then I get `Ticker("AAPL")` and `Weight(0.4)` respectively. Two `Holding`s with the same ticker + weight compare equal.
- [ ] **Scenario 2 (Sad Path):** Given a `Weight` outside `[0, 1]`, When I construct a `Holding`, Then `InvalidWeightError` is raised at construction time (fail-fast).
- [ ] **Edge Case (Mandatory):** If two `Holding`s are constructed with the same `Ticker`, equality still holds (no implicit duplicate rejection at the value-object level — duplicates are rejected at the aggregate level by `task-006`'s invariant).

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** N/A.

## Out of Scope

- The `Portfolio` aggregate itself (`task-006`).
- YAML / inline parsing (`task-007`).

## Deliverables

- `src/monte_carlo_risk/domain/portfolio/__init__.py`
- `src/monte_carlo_risk/domain/portfolio/holding.py` — `@dataclass(frozen=True, slots=True) class Holding(ticker: Ticker, weight: Weight)` with `__eq__` and `__hash__`.
- `tests/unit/domain/portfolio/test_holding.py` — covering happy + sad + duplicate scenarios.
