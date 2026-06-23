# Task 027 — Benchmark Gate (NFR-1: P50 ≤ 10 s, P95 ≤ 30 s)

**Epic:** epic-006-run-pipeline-quality
**Layer:** Defense
**Sprint:** 07
**Depends on:** task-024
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## Context

The build-breaking latency gate. Uses pytest-benchmark to time the full `simulate` run; fails CI if P50 exceeds 10 s or P95 exceeds 30 s on the pinned CI image. Traces to Story 6.3.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given the default `simulate` run, `When` pytest-benchmark runs 10 iterations, `Then` median ≤ 10 s and 95th percentile ≤ 30 s on the pinned CI Linux image (Ubuntu 22.04 + Python 3.12 + numpy from PyPI). The CI job `benchmark` is green.
- [ ] **Scenario 2 (Sad Path):** Given a developer accidentally adds an O(n²) operation in the path generator (e.g., a nested loop), `When` the benchmark job runs, `Then` it fails with a clear "P95 = 47 s, exceeds 30 s budget" message and the offending benchmark is highlighted in the output.
- [ ] **Edge Case (Mandatory):** The benchmark runs **only in CI** (not on every local `pytest` invocation), to keep the dev loop under 30 s. Local runs are tagged with `@pytest.mark.benchmark` and excluded by default; CI invokes pytest with `--benchmark-only --benchmark-enable`. A test asserts the marker is correctly applied.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** pytest-benchmark's output is captured to a `benchmarks/` directory in CI artifacts.
- [ ] **Contract Tests:** N/A.

## Out of Scope

- Profile-guided optimization work (only triggered after a regression).
- Cross-machine benchmarks (asserted on the pinned CI image only).
- Memory / CPU benchmarks (latency only in v1).

## Deliverables

- `tests/benchmark/test_simulate_benchmark.py` — `pytest-benchmark` test of `RunSimulation.execute()` with default parameters.
- Extension to `.github/workflows/ci.yml` — adds a `benchmark` job that runs `pytest tests/benchmark/ --benchmark-only --benchmark-enable --benchmark-min-rounds=10 --benchmark-columns=median,99th`, then asserts thresholds via `pytest-benchmark`'s `--benchmark-compare-fail` (or a simple `jq` filter on the JSON output).
- `benchmarks/README.md` — explains the gate, the CI image spec, and how to investigate regressions.
- New `pyproject.toml` dev dependency: `pytest-benchmark>=4.0`.
