# ADR-002 — `numpy` Whitelisted as a Domain Primitive

- **Status:** Accepted
- **Date:** 2026-06-23
- **Deciders:** jcarloshg
- **Source:** `00.defining.md` §3 Layer Enforcement; ADR-001 forbidden-import list.

## Context

ADR-001 defines a strict forbidden-import list for `domain/`. The most uncomfortable entry on that list is **`numpy`** — the project is a Monte Carlo simulator, and the math (random sampling, vectorized path generation, percentile computation) is overwhelmingly expressed in `numpy.ndarray` operations.

Two readings of "domain purity" are possible:

- **Strict reading.** `numpy` is a third-party library; therefore it is infrastructure. The domain must express its math in pure Python (`array.array`, `statistics`, hand-written vector loops) and have `infrastructure/numpy_adapter.py` translate to/from `ndarray` at the boundary.
- **Pragmatic reading.** `numpy` is the language the math is written in. Forbidding it in domain would force a translation layer that adds latency, bugs, and zero architectural value for a single-process CLI. `matplotlib`, in contrast, is genuinely infrastructure (it produces I/O artifacts and touches the filesystem via the rendering backend), so it stays forbidden.

## Options

1. **Strict reading.** Domain uses pure Python only; `numpy` is hidden behind an adapter. Most "pure" but cosmetically expensive — vectorized Monte Carlo over 10,000 paths in pure Python is ~50× slower.
2. **Pragmatic reading.** `numpy` is whitelisted as a domain primitive; `matplotlib` and HTTP/IO libs remain forbidden. ADR-001's forbidden list is the source of truth.
3. **No `numpy` at all.** Use `statistics` and Python lists. Fails the NFR-1 latency budget (P50 ≤ 10 s for 10k paths).

## Decision

**Option 2: pragmatic reading.**

- `numpy` is permitted inside `domain/`. It is treated as a **mathematical primitive**, like `math.sin()` or `decimal.Decimal`.
- The forbidden-import list in ADR-001 is updated to reflect this: `numpy` is not in the forbidden list.
- `matplotlib` remains forbidden in `domain/`. Chart rendering is an infrastructure concern that lives behind a `Visualization` port (see ADR-005 and ADR-001).
- This decision is recorded here so a future contributor is not surprised when `import numpy as np` appears in `domain/simulation/path_generator.py`.

## Consequences

**Positive.**
- The NFR-1 latency budget is achievable. A vectorized 10k × 252 path generation runs in < 2 s on a modern laptop; the same in pure Python takes ~100 s.
- Domain code reads like the math it represents (`np.percentile(terminal_wealth, 5)` is direct VaR(95%)).
- No translation layer between domain and the underlying math primitive.

**Negative.**
- Domain code is coupled to `numpy`. If the project ever switches to `jax` or `cupy`, domain modules change. Mitigated by keeping domain-numpy usage narrow (array creation, reductions, random sampling — no advanced indexing tricks).
- Slightly blurs "pure" domain modeling. Mitigated by this ADR being explicit and discoverable.

**Supersedes.** None.
