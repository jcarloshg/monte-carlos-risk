# Epic 002: Portfolio — Declare and Validate Holdings

**Status:** Ready
**Bounded Context:** Portfolio
**Sequence Order:** 2 of 6 (Foundation)
**Estimated Sprints:** 1

> The first user-facing capability: a user can declare a portfolio (tickers + weights) in YAML or inline CLI syntax, and the tool can validate it without running a simulation. Establishes the canonical error envelope's first real use case and the first Domain aggregate with invariants.

## 1. Business Context & Value

- **Why are we building this?** Every Monte Carlo run needs a portfolio. Validating weights-sum-to-1.0 and other invariants *before* the expensive simulation saves minutes of wasted compute per misconfigured run. Also gives users a fast feedback loop (`< 1 s`) for portfolio edits.
- **Success Metrics:**
  - `monte-carlo validate-portfolio --portfolio tests/fixtures/valid_portfolio.yaml` exits 0 in **< 1 s** and prints a JSON report.
  - `monte-carlo validate-portfolio --portfolio tests/fixtures/invalid_weights.yaml` exits 2 in **< 1 s** and prints exactly one canonical JSON error with `error_code = "weights_sum_must_equal_one"`.
  - 100% of invariant violations from `00.defining.md` §2 Bounded Contexts table are covered by unit tests.

## 2. Architectural Scope (C4 Level 2)

- **Containers Touched:** `Portfolio` aggregate (`domain/portfolio/`), `Portfolio.from_yaml()` and `Portfolio.from_inline()` factories, `validate-portfolio` use case (`application/use_cases/`), `validate-portfolio` CLI command (`interface/cli/commands/`).
- **External Dependencies:** PyYAML (read-only) for YAML parsing. Used in `infrastructure/`.
- **Database Impact:** None (ADR-009).

## 3. Strict "Out of Scope"

- **Short positions / leverage / margin** — weights are constrained to `[0, 1]`.
- **Multi-currency portfolios** — single base currency per portfolio.
- **Portfolio rebalancing / update** — once parsed, the portfolio is immutable in v1.
- **Persistent portfolio library** — v1 portfolios live as files or inline strings; no DB.
- **Real market-data integration** — Epic 003.
- **`simulate` command end-to-end** — Epic 003.

## 4. Non-Functional Requirements (NFRs)

- **NFR-1 (latency):** `validate-portfolio` P95 ≤ 1 s on a portfolio of ≤ 100 holdings (well within the global budget).
- **NFR-2 (test budget):** unit suite for this Epic ≤ 2 s.
- **NFR-6 (error contract):** every validation failure emits exactly one canonical JSON error line; the error code is one of the `cli-contract.yaml` enum values.
- **NFR-3 (domain purity):** `domain/portfolio/` has zero forbidden imports (linter passes).

## 5. Required Technical Artifacts (Definition of Ready)

- [ ] C4 Container Diagram approved. ✅ (unchanged from Epic 001)
- [ ] CLI contract section approved. ✅ `100.planning/contracts/cli-contract.yaml` §`commands[validate-portfolio]` and §`schemas.portfolio_schema` and §`schemas.portfolio_validation_report` are frozen.
- [ ] UI/UX designs approved. **N/A — CLI-only per ADR-005.**
- [ ] Event schemas merged. ✅ `PortfolioDefined` event payload is frozen in `100.planning/contracts/events.schema.json`.

## 6. User Stories (BDD)

- **Story 2.1:** Validate a well-formed portfolio file.
  - *Scenario:* `Given` a YAML file with 3 holdings summing to 1.0, `When` I run `monte-carlo validate-portfolio --portfolio portfolio.yaml`, `Then` exit code is 0 and the JSON report shows `"valid": true` and an echo of the parsed portfolio.
  - *Edge Case placeholder:* handled in `task-006`/`task-009`.
- **Story 2.2:** Reject a portfolio whose weights do not sum to 1.0.
  - *Scenario:* `Given` a YAML file with 3 holdings summing to 0.95, `When` I run `monte-carlo validate-portfolio`, `Then` exit code is 2 and stderr is exactly one JSON error with `error_code = "weights_sum_must_equal_one"`.
  - *Edge Case placeholder:* handled in `task-009`.
- **Story 2.3:** Validate an inline portfolio string.
  - *Scenario:* `Given` `--portfolio 'AAPL:0.4,MSFT:0.3,GOOG:0.3'`, `When` I run `monte-carlo validate-portfolio`, `Then` exit code is 0 and the parsed portfolio matches the inline spec.
  - *Edge Case placeholder:* handled in `task-007`.
