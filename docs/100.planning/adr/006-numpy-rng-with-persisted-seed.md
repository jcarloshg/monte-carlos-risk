# ADR-006 — NumPy RNG with Persisted Seed for Byte-for-Byte Reproducibility

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Source inputs:** `docs/00.defining.md` Q1.6 (seed invariant), Q3.7
  (idempotency / replay), 200-Q1.2 (seed as `uint64`)

## Context

A Monte Carlo engine is only scientifically useful if runs are reproducible.
The defining doc requires the `seed` to be (a) persisted on every run and
(b) sufficient to reconstruct the run byte-for-byte (Defining Q3.7, 200-
Q1.2). We need to choose how randomness enters the domain.

## Options Considered

1. **`np.random.default_rng()` called directly inside the engine.** Easiest
   to write. Breaks pure domain (import-linter rule from ADR-002 also flags
   it).
2. **Inject `RNG` Protocol port.** Domain code calls `rng.normal(...)` on
   an injected `RNG`. Production adapter is `NumpyGenerator`; test adapter
   is `SeededGenerator` with deterministic output. `seed` is part of the
   `SimulationProfile` Pydantic model and is persisted.
3. **`random` stdlib.** Too slow for `O(paths × horizon)` inner loops.

## Decision

**Option 2.** A `RNG` Protocol lives in `src/application/ports/rng.py`:

```python
class RNG(Protocol):
    def normal(self, loc: float, scale: float, size: tuple[int, ...]) -> np.ndarray: ...
    def integers(self, low: int, high: int, size: tuple[int, ...]) -> np.ndarray: ...
    def choice(self, a: np.ndarray, size: tuple[int, ...], replace: bool) -> np.ndarray: ...
```

`NumpyGenerator` wraps `numpy.random.Generator` constructed from
`numpy.random.SeedSequence(seed)`. The seed is part of `SimulationProfile`
(Pydantic) and is the immutable `seed` field of `SimulationRun` (200-Q1.5
invariant). A run cannot transition to `COMPLETED` without the seed on
disk.

Replay is verified by an integration test: given the persisted seed, the
output `metrics.json` and `events.jsonl` are byte-identical to the original
(modulo `correlationId` and `occurredAt`, which are stripped before
comparison).

## Consequences

**Positive**
- Domain stays pure. `mypy --strict` checks the Protocol conformance.
- Tests use a seeded `Generator(42)` — no `mock.patch`, no hidden state.
- "Reproduce this run" is a single CLI flag: `--replay <runId>` reads the
  seed from the prior run directory.

**Negative**
- One extra layer of indirection. Mitigated by the Protocol being 3
  methods.
- `numpy.random.Generator` API is frozen per NumPy minor; a major NumPy
  rewrite would touch this adapter. Acceptable.

**Reversibility**
- Trivial — replace `NumpyGenerator` with a different implementation
  (e.g., `RandomGenerator` using `pcg64` directly).
