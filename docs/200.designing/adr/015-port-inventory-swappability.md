# ADR-015 — Port Inventory & Swappability Rule (≥ 2 Adapters per Port)

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Supersedes:** none
- **Source inputs:** `architecture/hexagonal.md` (Port inventory),
  ADR-002 (hexagonal layout), `docs/200.designing/02.designing.md` §2.2.1

## Context

The Designing playbook (§2.2 + Best Practices) states:

> "Every Port has at least two adapters at design time: one real (Postgres,
> SQS) and one in-memory (for tests). If a Port only has one implementation,
> the abstraction is probably wrong."

This is a **design-time invariant**, not a coding-time check. We need to:

1. **Freeze the 5 Ports** that the application layer consumes.
2. **Freeze the 2-adapter pairing** for each Port (production + in-memory).
3. **Document the review rule** so a future PR that adds a new Port is
   blocked by code review unless it ships with the in-memory adapter.

## Options Considered

1. **No swappability rule.** Trust the developer to add adapters as
   needed. Result: Ports with one adapter accumulate as the codebase
   grows, and the abstraction rots.
2. **Rule + frozen inventory.** Document the rule and freeze the inventory
   as part of the Architectural Blueprint. Code review enforces the rule.
3. **Rule + mechanical check.** Add a pytest plugin that asserts every
   Protocol has ≥ 2 concrete subclasses. Heavy machinery for a small
   repo.

## Decision

**Option 2.** The rule and the inventory are both frozen in this ADR +
`architecture/hexagonal.md`. Code review enforces the rule socially; the
small repo size makes option 3 impractical.

## Frozen Port inventory (5 ports)

| # | Port | Production adapter | In-memory adapter |
|---|---|---|---|
| 1 | `ReturnRepository` | `CsvReturnRepository` | `InMemoryReturnRepository` |
| 2 | `SimulationResultStore` | `JsonlEventWriter` | `InMemoryEventStore` |
| 3 | `RNG` | `NumpyGenerator` | `SeededGenerator` |
| 4 | `Clock` | `SystemClock` (in shared_kernel) | `FakeClock` |
| 5 | `Renderer` | `MatplotlibRenderer` | `NullRenderer` |

The Protocol shape for each Port is frozen in
`architecture/hexagonal.md` §2. Any change to a Protocol is a breaking
change to all its adapters and to every use case that consumes it.

## The rule (frozen)

> **If a Port has only one adapter, the abstraction is probably wrong.**
>
> Every PR that introduces a new Port MUST also introduce at least one
> in-memory / test adapter in the same PR. The in-memory adapter lives
> under `tests/adapters/` and is referenced by at least one unit test
> in the same PR.

## Code-review checklist (PR template addition)

When a PR touches `src/application/ports/`, the PR description must
answer:

- [ ] If a new Port was added: which test adapter was added in the same PR?
- [ ] If a Port signature changed: which adapters were updated and which
      use cases were re-typed?
- [ ] If an adapter was deleted: was the Port removed too? (Or replaced
      with what?)

## Consequences

**Positive**
- The hexagonal abstraction stays meaningful (no Port accumulates a
  single concrete implementation).
- Unit tests are trivially fast — every use case can be exercised
  against the in-memory adapters without any I/O.
- The future ACL adapter (e.g., `MarketDataAcl` per ADR-001) is a
  third adapter behind the same Port; the rule says ≥ 2, not exactly 2.

**Negative**
- The rule is enforced socially, not mechanically. A future contributor
  who skips the in-memory adapter can land the PR without CI catching it.
  Mitigation: import-linter (ADR-002) catches the downstream symptom
  (use cases testing with real I/O), so the rule has a safety net.

**Reversibility**
- Fully reversible by removing this ADR. The Port inventory would
  remain valid; only the swappability rule would be relaxed.