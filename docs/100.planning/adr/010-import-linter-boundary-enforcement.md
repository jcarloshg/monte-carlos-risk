# ADR-010 — Import-Linter + mypy --strict as the Architectural Boundary Gate in CI

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Source inputs:** `docs/00.defining.md` 300-Q1.2, 300-Q1.4, ADR-002

## Context

ADRs 002 and 008 already mandate `import-linter` and `mypy --strict`. This
ADR fixes the **CI integration**: how the architectural boundary is
enforced every PR, what is blocking, and what is advisory.

## Options Considered

1. **No CI gate.** Trust the developer. Fails fast (i.e., fails on first
   bug).
2. **Lint + typecheck as blocking CI stages; import-linter as advisory.**
   Lower friction. Lets domain/infrastructure drift sneak through.
3. **All three as blocking.** Friction on every PR but guarantees the
   hexagonal boundaries hold.

## Decision

**Option 3.** The CI pipeline (`.github/workflows/ci.yml`) runs the
following stages, **all blocking** on every PR and on every push to
`main`:

1. `ruff format --check`
2. `ruff check`
3. `mypy --strict`
4. `pytest -m "not slow and not benchmark and not mutation"` (unit +
   integration + architectural)
5. `import-linter` (architectural boundary contract from ADR-002)
6. `make contracts` (regenerate JSON Schemas; fail if `git status` shows
   a diff)
7. `docker build` (confirms the Dockerfile still resolves dependencies)
8. CLI smoke test (runs `docker compose up` with the default scenario)

Nightly (not blocking on PR):
- `pytest -m benchmark` (performance budget asserts from Defining 200-Q2.2)
- `mutmut run --paths src/domain/simulation/` (mutation score ≥ 70%)

## Consequences

**Positive**
- A PR that violates the hexagonal boundary cannot merge. The contract
  is the contract.
- The JSON Schema diff gate ensures `docs/contracts/` and Pydantic
  models never drift (ADR-004).
- Nightly jobs catch perf regressions without slowing PR feedback.

**Negative**
- Slower PR feedback (~3–5 min total). Acceptable for a learning repo
  with one author.

**Reversibility**
- Each stage can be downgraded from blocking to advisory by deleting
  the corresponding `needs:` chain in the workflow file.
