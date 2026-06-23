# ADR-012 — Determinism & RNG Strategy

- **Status:** Accepted
- **Date:** 2026-06-23
- **Deciders:** jcarloshg
- **Source:** NFR-4 (reproducibility), NFR-5 (idempotency), NFR-1 (P50 ≤ 10 s, P95 ≤ 30 s); `architecture/data-flow.md` diagram #4.
- **Related:** Planning §1 Bounded Contexts (Simulation owns RNG); ADR-007 (hexagonal package layout).

## Context

The Monte Carlo simulation is the project's core compute. Reproducibility (NFR-4) requires that two runs with the same `(seed, portfolio, n_paths, horizon, mock_data_version)` produce **bit-identical outputs**. This is harder than it looks because:

1. `numpy.random` has multiple legacy APIs (`np.random.seed`, `np.random.RandomState`, `numpy.random.Generator`) with different determinism guarantees and cross-version behavior.
2. Parallelism (multi-threaded BLAS, multi-process path generation) introduces non-determinism if RNG streams are shared naively.
3. Floating-point reduction order is not guaranteed across BLAS implementations or platforms; summing `path[:, -1]` in different orders can produce different last-bit results.

A consistent RNG strategy is needed so that the contract in `architecture/data-flow.md` diagram #4 holds.

## Options

1. **`numpy.random.seed` (legacy).** Sets a global RNG state. Not thread-safe, not parallel-safe, deprecated since NumPy 1.17 in favor of `Generator`. Rejected.
2. **`numpy.random.RandomState` (legacy, MT19937).** Older API, still supported but not the recommended path forward. Rejected.
3. **`numpy.random.default_rng(seed)` (modern, PCG-64).** The recommended NumPy 1.17+ API. Returns a `Generator` instance. Thread-safe per-instance (not across instances). Uses PCG-64 by default, which has good statistical properties and is well-tested for determinism.
4. **`numpy.random.SeedSequence` + spawn.** Modern, designed for parallel streams. Bit more ceremony but enables per-path antithetic sampling deterministically.

## Decision

**Option 4: `numpy.random.SeedSequence` spawning child `Generator`s via `default_rng`.**

Concrete shape:

```python
# application/use_cases/run_simulation.py (pseudocode)
def execute(self, parameters: SimulationParameters) -> PathSet:
    parent_ss = np.random.SeedSequence(parameters.seed)
    # Spawn one child Generator per path for independence.
    child_seeds = parent_ss.spawn(parameters.n_paths)
    path_generators = [np.random.default_rng(s) for s in child_seeds]
    # ... use one generator per path ...
```

### Why SeedSequence spawning

- **Determinism.** Two runs with the same seed produce the same `SeedSequence`, the same child seeds, and therefore the same per-path generators and the same paths. Bit-identical outputs modulo floating-point reduction order.
- **Parallel-safety.** Each path has its own `Generator` instance; there is no shared state. A future parallelization (e.g., `concurrent.futures` over paths) can be added without breaking determinism.
- **Statistical quality.** PCG-64 is well-tested and avoids known weaknesses of MT19937.
- **Cross-version stability.** NumPy's PCG-64 bit generator is stable across minor versions; the legacy MT19937 was not always bit-stable.

### Where the RNG lives

The `DeterministicRNG` Protocol lives in `application/ports/rng.py`. Its v1 implementation `NumpyRNG` lives in `infrastructure/rng/numpy_rng.py` and is composed at startup in `interface/cli/app.py`. The domain layer receives a `DeterministicRNG` instance through the use case; it never imports `numpy.random` directly.

```python
# application/ports/rng.py
class DeterministicRNG(Protocol):
    @property
    def seed(self) -> int: ...
    def uniform(self, low: float = 0.0, high: float = 1.0, size: int | tuple[int, ...] = 1) -> np.ndarray: ...
    def normal(self, loc: float = 0.0, scale: float = 1.0, size: int | tuple[int, ...] = 1) -> np.ndarray: ...
    def integers(self, low: int, high: int | None = None, size: int | tuple[int, ...] = 1) -> np.ndarray: ...
    def spawn(self, child_seed: int) -> "DeterministicRNG": ...

# infrastructure/rng/numpy_rng.py
class NumpyRNG:
    def __init__(self, seed: int):
        self._seed = seed
        self._generator = np.random.default_rng(np.random.SeedSequence(seed))

    @property
    def seed(self) -> int:
        return self._seed

    # ... delegate uniform/normal/integers/spawn to self._generator ...
```

### Determinism for non-numpy operations

Three sources of non-determinism exist outside numpy:

- **matplotlib rendering.** Mitigated by:
  - `matplotlib.use("Agg")` set before any pyplot import (no interactive backend).
  - A pinned `matplotlib.rcParams` set (no random style application).
  - PNG metadata timestamps stripped or pinned via Pillow's `PngImagePlugin` (`pilinfo` metadata).
- **Filesystem ordering.** Mitigated by deterministic artifact filenames (`{run_id}_paths.png`) and sorted-glob reads in `MockMarketDataSource`.
- **JSON serialization.** Mitigated by sorting keys (`json.dumps(obj, sort_keys=True)`) and a fixed indent.

These mitigations are encoded in `architecture/data-flow.md` diagram #4 §Determinism guarantees and asserted by the `tests/integration/test_byte_identical_rerun.py` integration test (a CI job that runs `simulate` twice with the same inputs and `diff -r`s the output directories).

### Floating-point determinism caveat

Cross-platform reproducibility (Linux vs macOS vs Windows; different BLAS builds) is **not** guaranteed due to floating-point reduction-order differences in numpy reductions. NFR-4 is asserted **per-platform**: CI runs on a pinned Linux image. macOS and Windows runs are best-effort reproducible, not asserted. This is recorded as a known limitation in the README.

## Consequences

**Positive.**
- Reproducibility (NFR-4) is achievable per-platform with a single `seed` flag.
- The `DeterministicRNG` Protocol allows the v1 implementation to be swapped (e.g., for `cupy` on GPU) without touching the domain.
- Per-path generators enable future parallelization without breaking determinism.

**Negative.**
- Cross-platform byte-identical reproducibility is not asserted. Acceptable for an educational tool.
- The `NumpyRNG` adapter is tightly coupled to `numpy`'s PCG-64 bit generator. A future migration to `cupy` or `jax` requires updating the adapter but not the domain.

**Supersedes.** None.
