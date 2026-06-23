# ADR-002 — Hexagonal / DDD Layout Enforced by Import-Linter Architectural Test

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Source inputs:** `docs/00.defining.md` 300-Q1.4, 300-Q2.1

## Context

A flat Python package lets `domain/` files `import` from `infrastructure/`,
which silently couples business rules to I/O concerns (matplotlib, the
filesystem, click). This is the classic "anemic domain + service layer that
does everything" anti-pattern. Without a structural enforcement, the boundary
degrades within a week.

## Options Considered

1. **Convention only.** Document the rule in `CONTRIBUTING.md`. Easy to
   ignore; no machine-checked gate.
2. **import-linter + pytest-arch.** Declarative contract files describe
   forbidden import directions; CI fails on violation. Requires ~30 lines of
   `.importlinter` config.
3. **Custom AST check.** Hand-rolled script in `tests/architectural/`. Cheap
   to write, expensive to maintain as Python evolves.

## Decision

**Option 2.** Adopt `import-linter` with the following contract (canonical
form lives in `.importlinter`):

```
layers:
  - name: domain
    type: forbidden
    modules:
      - src.domain
    forbidden:
      - src.infrastructure
      - src.interfaces
      - pandas
      - matplotlib
      - click
      - typer

  - name: application
    type: forbidden
    modules:
      - src.application
    forbidden:
      - src.infrastructure
      - src.interfaces

  - name: shared_kernel
    type: independent
    modules:
      - src.domain.shared_kernel
```

The lint runs in CI as a blocking stage (see ADR-010).

## Consequences

**Positive**
- Domain code cannot accidentally import `pathlib`, `matplotlib`, or
  `click`. `mypy --strict` catches the rest (Protocol conformance).
- New contributors (or future-self) cannot "just add a `print`" in the
  domain layer without breaking the build.
- Refactor cost is zero — the contract is declarative.

**Negative**
- One more CI dependency. `import-linter` is well-maintained and small.
- The contract is verbose to extend; mitigated by the `.importlinter` file
  being the single source.

**Reversibility**
- Fully reversible by deleting `.importlinter`. No production code changes.
