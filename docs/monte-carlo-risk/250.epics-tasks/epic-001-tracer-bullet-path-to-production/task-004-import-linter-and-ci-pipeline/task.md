# Task 004 — `import-linter` Config + CI Pipeline

**Epic:** epic-001-tracer-bullet-path-to-production
**Layer:** Defense
**Sprint:** 01
**Depends on:** task-003
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## Context

The CI pipeline that the Tracer Bullet promises in Story 1.3. Encodes the forbidden-import graph from `200.designing/architecture/hexagonal.md` §Linter Contract and adds the four CI jobs that gate every later PR. Traces to Stories 1.1 and 1.3.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given the `.importlinter` config from `hexagonal.md` is dropped at the repo root and `domain/`, `application/`, `infrastructure/`, `interface/` packages exist, When CI runs `lint-imports`, Then exit code is 0.
- [ ] **Scenario 2 (Sad Path):** Given a developer adds `import matplotlib` inside `src/monte_carlo_risk/domain/portfolio/portfolio.py`, When CI runs, Then the `domain-purity` job fails with the offending import and the line number.
- [ ] **Edge Case (Mandatory):** If the `.importlinter` config is missing or malformed, `lint-imports` MUST fail loudly with a non-zero exit and a clear error — it must NOT silently pass when the config is absent (silent pass would defeat the entire CI gate).

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** CI job names follow the convention `<job-name>` so logs are greppable.
- [ ] **Contract Tests:** The CI workflow's `docker-smoke` job runs `docker compose run --rm monte-carlo describe-mock-data` and asserts exit 0 + valid JSON — this is the first end-to-end contract test, even though formal contract testing lands in Epic 002.

## Out of Scope

- Pact / consumer-driven contract tests (N/A — no producer/consumer service boundary in v1).
- Load / stress / chaos testing (N/A — single-machine CLI; benchmark gate is Epic 006 / task-027).
- Codecov / coverage thresholds (deferred — added if coverage drops below 80% in any Epic).

## Deliverables

- `.importlinter` config exactly matching `200.designing/architecture/hexagonal.md` §Linter Contract (3 contracts: `domain-purity`, `application-boundary`, `no-orm-leak`).
- `.github/workflows/ci.yml` with four jobs in order:
  1. `lint` — `ruff check . && ruff format --check .`
  2. `domain-purity` — `lint-imports`
  3. `test` — `pytest tests/unit/ -v --tb=short`
  4. `docker-smoke` — `docker compose build && docker compose run --rm monte-carlo describe-mock-data` (asserts exit 0 and stdout matches `mock_data_descriptor` schema via a small `jq` filter)
- `mypy.ini` with `strict = True` and `mypy src/monte_carlo_risk` added to the `lint` job.
- `tests/unit/test_smoke.py` (the placeholder from `task-001`) extended to assert that all four CI jobs would pass locally (a "local CI" sanity test).
- `CONTRIBUTING.md` with a one-paragraph note on the four CI jobs and the rule "no commit lands with a red CI."
