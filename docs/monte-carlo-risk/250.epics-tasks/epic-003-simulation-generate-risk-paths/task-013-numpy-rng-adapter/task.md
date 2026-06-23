# Task 013 — `NumpyRNG` Adapter

**Epic:** epic-003-simulation-generate-risk-paths
**Layer:** Infrastructure
**Sprint:** 03
**Depends on:** task-004
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## Context

Implements the `DeterministicRNG` Protocol from `application/ports/rng.py` using `numpy.random.SeedSequence` spawning per ADR-012. The core determinism primitive for NFR-4.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given `NumpyRNG(seed=1729)`, When I call `.normal(loc=0.0, scale=0.01, size=(252,))`, Then a numpy array of shape `(252,)` is returned with values from N(0, 0.01).
- [ ] **Scenario 2 (Sad Path):** Given `NumpyRNG(seed=1729)`, When I call `.normal(loc=0.0, scale=-1.0, size=(10,))` (negative scale), Then `InvalidRngParameterError` is raised. `numpy.random` itself raises but we wrap to a typed exception.
- [ ] **Edge Case (Mandatory):** Given the same seed, two `NumpyRNG` instances constructed in different processes on the same platform produce **identical** `.normal(size=(10000,))` outputs bit-for-bit. This is the per-platform reproducibility assertion required by NFR-4 (cross-platform is best-effort per ADR-012 §Floating-point determinism caveat).

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** Adds `tests/contract/test_rng_contract.py` — parameterized against any `DeterministicRNG`. Asserts that `(NumpyRNG(1729), NumpyRNG(1729))` produce identical samples.

## Out of Scope

- The `SimulationRun` aggregate that consumes the RNG (`task-014`).
- GPU RNG (`cupy`) — N/A for v1.
- Different bit generators (MT19937, Philox) — PCG-64 only in v1 per ADR-012.

## Deliverables

- `src/monte_carlo_risk/infrastructure/rng/numpy_rng.py` — `class NumpyRNG` implementing `DeterministicRNG`. Internally: `self._ss = np.random.SeedSequence(seed); self._generator = np.random.default_rng(self._ss)`.
- `src/monte_carlo_risk/domain/simulation/exceptions.py` (extend) — `InvalidRngParameterError`.
- `tests/unit/infrastructure/rng/test_numpy_rng.py` — happy + sad + cross-instance equality edge case.
- `tests/contract/test_rng_contract.py` — contract test parametrized over `NumpyRNG`.
