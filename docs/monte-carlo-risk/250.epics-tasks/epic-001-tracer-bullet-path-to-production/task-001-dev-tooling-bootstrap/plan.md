# Plan: task-001 — Dev Tooling Bootstrap

**Source task:** docs/monte-carlo-risk/250.epics-tasks/epic-001-tracer-bullet-path-to-production/task-001-dev-tooling-bootstrap/task.md
**Plan file:** docs/monte-carlo-risk/250.epics-tasks/epic-001-tracer-bullet-path-to-production/task-001-dev-tooling-bootstrap/plan.md
**Layer:** Infra (L1)
**Epic:** epic-001-tracer-bullet-path-to-production
**Sprint:** 01
**Owner:** jcarloshg
**Depends on:** none (first task in the chain)
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## 1. Feature Summary

Task 001 is the first task of the Tracer Bullet. Its purpose is to land the dev-time toolchain so every subsequent task (002 → 028) starts on a working machine in under five minutes. Concretely this task ships `pyproject.toml` (Python ≥ 3.12, `[dev]` extras), a `Dockerfile` based on `python:3.12-slim`, a `docker-compose.yml` with a single `monte-carlo` service, a `Makefile` exposing `bootstrap`, `test`, `lint`, `format`, `docker-build`, `docker-smoke`, a `.gitignore`, a `.python-version` pinned to 3.12, an empty `src/monte_carlo_risk/__init__.py` exposing `__version__ = "0.1.0"`, and a one-line `tests/test_smoke.py` that asserts `True`.

The task lives in **L1 Infra** (no domain logic, no transport, no contract). It is the foundation that lets tasks 002 (hexagonal layout), 003 (CLI stub), and 004 (`.importlinter` + CI) build on top without paying the bootstrap tax. The bootstrap MUST succeed even when Docker is missing (Edge Case): `make bootstrap` runs lint + tests without Docker; the Docker image is built only by `make docker-build`.

## 2. Pre-Flight Checks

- [x] **None** — first task in the chain; no `Depends on:` blocks.
- [x] Frozen design artifacts present: ADRs (folder `docs/monte-carlo-risk/100.planning/adr/`), OpenAPI/CLI contract (`docs/monte-carlo-risk/100.planning/contracts/cli-contract.yaml`), C4 Container (`docs/monte-carlo-risk/100.planning/diagrams/c4-container.md`), hexagonal port map (`docs/monte-carlo-risk/200.designing/architecture/hexagonal.md`).
- [ ] **BLOCKER — Repo + CI baseline missing.** `pyproject.toml`, `Makefile`, `Dockerfile`, `docker-compose.yml`, `.github/workflows/` are all absent. This task CREATES them, so this is the bootstrapping step itself, not a blocker for the work — but flagging for visibility: there is nothing to lint or test until this PR merges.
- [ ] **BLOCKER — Feature flag service absent.** Per task `Out of Scope`, no flags are needed for v1 (single-process CLI). Recorded as N/A in §9; no registration needed.
- [x] No architectural drift detected (no code yet, nothing to drift from).

**Local environment note (non-blocking):** `.python-version` in the repo currently reads `3.14.6`. The task spec requires pinning to `3.12`. pyenv will install 3.12 on demand; system Python 3.14.6 still satisfies the Sad-Path guard (`>= 3.12` and not ≤ 3.11). Surface this in §8.

## 3. Setup

1. Branch off `main`: `task-001-dev-tooling-bootstrap`.
2. Confirm Python interpreter available locally (≥ 3.12). If using pyenv: `pyenv install 3.12` (only if the system Python is ≤ 3.11 — see Sad Path).
3. Confirm Docker availability is **not required** for the bootstrap itself. Run `docker --version` only to know whether `make docker-build` will be exercisable locally; if missing, the bootstrap MUST still pass.
4. Confirm `make` and `git` are on PATH.
5. No secrets, no feature flags, no external services to pre-register before coding starts.

## 4. Implementation Steps (Ordered)

### Step 4.1 — Author `pyproject.toml` (project metadata + `[dev]` extras)

- File(s) to create: `pyproject.toml`
- What to write:
  - `[build-system]` using `setuptools>=68` (PEP 517).
  - `[project]` with `name = "monte-carlo-risk"`, `version = "0.1.0"`, `requires-python = ">=3.12"`, `readme = "README.md"`.
  - `[project.optional-dependencies.dev]` listing exactly: `pytest`, `pytest-cov`, `ruff`, `mypy`, `import-linter`, `structlog`, `typer`, `numpy`, `matplotlib`.
  - `[tool.setuptools.packages.find]` rooted at `src` (`where = ["src"]`, `include = ["monte_carlo_risk*"]`).
  - Minimal `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `addopts = "-q"`).
  - Stub `[tool.ruff]` and `[tool.mypy]` sections so Step 4.2/4.3 do not trip on missing config (line-length = 100; `[[tool.mypy.overrides]] module = []` for now).
- Verify: `python -c "import tomllib; tomllib.loads(open('pyproject.toml').read())"` parses without error.

### Step 4.2 — Create the package skeleton + smoke test

- File(s) to create:
  - `src/monte_carlo_risk/__init__.py` containing `__version__ = "0.1.0"`.
  - `tests/__init__.py` (empty file).
  - `tests/test_smoke.py` with a single test:
    ```python
    def test_smoke() -> None:
        assert True
    ```
  - `tests/test_version.py` asserting `monte_carlo_risk.__version__ == "0.1.0"` (covers the bootstrap install path).
- Verify: `pip install -e ".[dev]"` then `pytest -q` → 2 passed in < 5 s (NFR-2 unit budget).

### Step 4.3 — Author the `Makefile` with all six targets

- File(s) to create: `Makefile`
- What to write:
  - `bootstrap` target:
    1. Resolve interpreter: prefer `python3.12` if on PATH, else `python3` ≥ 3.12; else fail with `Python 3.12 required`.
    2. `python -m pip install -U pip` then `pip install -e ".[dev]"`.
    3. `pre-commit install` (only if `.pre-commit-config.yaml` exists; this task does NOT create it — see Out-of-Scope).
    4. `pytest -q` (must be green before the target exits 0).
    5. Detect Docker: `command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1` → print "Docker available, run 'make docker-build' to build the image". If missing → print "Docker not available; 'make bootstrap' succeeded without Docker image." **Do not exit non-zero.**
  - `test` target: `pytest -q --cov=src/monte_carlo_risk --cov-fail-under=0` (cap to 0 for this task — real coverage gate arrives with task-002).
  - `lint` target: `ruff check src tests && ruff format --check src tests && mypy src`.
  - `format` target: `ruff check --fix src tests && ruff format src tests`.
  - `docker-build` target: `docker compose build` (best-effort; warn-and-skip if `docker compose` not installed).
  - `docker-smoke` target: `docker compose run --rm monte-carlo python -c "import monte_carlo_risk; print(monte_carlo_risk.__version__)"`.
- Verify: `make bootstrap` exits 0 in < 2 min on a clean clone (Scenario 1); `make lint` exits 0; `make test` reports 2 passed.

### Step 4.4 — Author the Docker assets

- File(s) to create:
  - `Dockerfile`:
    - `FROM python:3.12-slim`.
    - Set `ENV PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`, `PIP_NO_CACHE_DIR=1`.
    - Create non-root user `app` (`useradd --create-home --shell /bin/bash app`) and `WORKDIR /app`.
    - `COPY pyproject.toml README.md ./` then `COPY src ./src` then `RUN pip install --no-cache-dir -e ".[dev]"`.
    - `USER app`.
    - `ENTRYPOINT ["python", "-m", "monte_carlo_risk"]` (the package's `__main__.py` will arrive with task-003; for task-001 the entrypoint fails cleanly because there is no `__main__.py` yet — see Step 4.6 mitigation).
  - `docker-compose.yml`:
    - Single service `monte-carlo` building from `.`.
    - `image: monte-carlo-risk:dev`.
    - `stdin_open: true`, `tty: true` (so `describe-mock-data` later can attach).
    - `working_dir: /app`.
    - No volumes (CLI is stateless).
- Verify: `docker compose config` parses without error; `make docker-build` succeeds when Docker is present; `make docker-smoke` exits 0 (mitigated by Step 4.6 below).

### Step 4.5 — Author repo hygiene files

- File(s) to create:
  - `.gitignore` — exclude `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `output/`, `*.egg-info/`, `dist/`, `build/`, `.venv/`, `coverage.xml`, `.coverage`.
  - `.python-version` — pin to `3.12` (single line).
  - `.dockerignore` — exclude `.git`, `docs`, `.venv`, `*.md` (except README), `tests`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`.
- Verify: `git check-ignore -v __pycache__/ .pytest_cache/ output/` reports each path is ignored; `cat .python-version` returns `3.12`.

### Step 4.6 — Add a minimal `__main__.py` so the Docker entrypoint does not crash

- File(s) to create: `src/monte_carlo_risk/__main__.py`
- What to write:
  ```python
  from monte_carlo_risk import __version__

  if __name__ == "__main__":
      print(__version__)  # Tracer Bullet placeholder; replaced by Typer app in task-003
  ```
- Rationale: avoids `python -m monte_carlo_risk` failing with `No module named monte_carlo_risk.__main__` inside the container until task-003 lands. Stays inside the Out-of-Scope boundary (no Typer root, no CLI commands — just a version echo so the smoke test passes).
- Verify: `python -m monte_carlo_risk` prints `0.1.0`; `make docker-smoke` exits 0.

### Step 4.7 — Update README with the bootstrap one-liner

- File(s) to modify: `README.md`
- What to write: a "Quickstart" section documenting `make bootstrap && make test && make lint` (≤ 10 lines). Do NOT duplicate the epic or the planning docs.
- Verify: `grep -q "make bootstrap" README.md` exits 0.

## 5. Testing Strategy

- [ ] **Happy Path** (`Given a clean git clone … When I run make bootstrap Then …`):
  - Test file: `tests/test_smoke.py` (existing) **plus** a new shell-level acceptance script `scripts/ci_smoke_bootstrap.sh` invoked by CI/manual drill.
  - Function: `test_smoke` + the script's `assert_make_bootstrap_exits_zero_and_under_120s` step.
  - Asserts: `pip install -e ".[dev]"` succeeds, `pytest -q` exits 0, `make lint` exits 0, total wall-clock < 120 s.
- [ ] **Sad Path** (`Given Python 3.11 or earlier … When I run make bootstrap Then …`):
  - Test file: `tests/test_makefile_python_guard.py` (a unit test that imports the `bootstrap` recipe's Python-resolution logic — or, since Makefile cannot be unit-tested, a `tests/test_bootstrap_python_guard.py` driving a shell function extracted to `scripts/bootstrap_python_guard.sh`).
  - Function: `it('rejects Python 3.11 with a clear error')`.
  - Asserts: subprocess run of the guard with `PYTHON=python3.11` returns non-zero exit and stderr contains `"Python 3.12 required"`.
- [ ] **Edge Case — MANDATORY** (`If docker compose is unavailable … make bootstrap MUST still succeed …`):
  - Test file: `tests/test_bootstrap_without_docker.py`.
  - Function: `it('bootstrap succeeds when docker is absent')` — sets `PATH` to a temp dir without `docker`, invokes `scripts/bootstrap_python_guard.sh` (or runs the bootstrap recipe under `make -n` first, then exercises the install + pytest subset that does NOT require Docker).
  - Asserts: install + pytest pass; no call to `docker` is made; bootstrap exit code is 0; the "Docker not available" message is printed.

Test types per layer:
- L1 → No Testcontainers needed (no DB/cache/broker). The integration test is the `make bootstrap` shell script itself executed against a fresh `python -m venv` in CI.
- L2 → N/A (no domain code).
- L3 → N/A (no transport).
- L4 → N/A (defense layer arrives with task-004).
- L5 → N/A (delivery layer arrives with task-028).

## 6. PR + Merge

1. PR title: `task-001: Dev Tooling Bootstrap`.
2. PR description:
   - Link `docs/monte-carlo-risk/250.epics-tasks/epic-001-tracer-bullet-path-to-production/task-001-dev-tooling-bootstrap/task.md`.
   - Copy the three BDD scenarios (Happy / Sad / Edge) as the PR checklist.
   - Tick each `Task Breakdown` item as it lands (all five are `N/A — <reason>`).
3. Cap PR at ≈ 250 LOC; if larger, split the shell guard + tests into a stacked branch.
4. CI must be green: lint, unit. (The `domain-purity` job arrives with task-004 — not required for this PR.)
5. Reviewer focus: BDD AC, Out-of-Scope adherence (no Typer root, no `.importlinter`, no hexagonal directory tree), diff size. Architecture is enforced by the linter once task-004 lands.
6. Merge: **squash-merge to `main`**, delete the branch, mark `task-001` `Done` in `docs/monte-carlo-risk/250.epics-tasks/dependency-graph.md`.

## 7. Artifacts to Produce

- [ ] `pyproject.toml` (Step 4.1)
- [ ] `src/monte_carlo_risk/__init__.py` (Step 4.2)
- [ ] `src/monte_carlo_risk/__main__.py` (Step 4.6)
- [ ] `tests/__init__.py` (Step 4.2)
- [ ] `tests/test_smoke.py` (Step 4.2)
- [ ] `tests/test_version.py` (Step 4.2)
- [ ] `tests/test_bootstrap_python_guard.py` (Step 5 Sad Path)
- [ ] `tests/test_bootstrap_without_docker.py` (Step 5 Edge Case)
- [ ] `scripts/bootstrap_python_guard.sh` (extracted Python-version guard, reused by `Makefile`)
- [ ] `scripts/ci_smoke_bootstrap.sh` (Happy Path acceptance drill)
- [ ] `Makefile` (Step 4.3)
- [ ] `Dockerfile` (Step 4.4)
- [ ] `docker-compose.yml` (Step 4.4)
- [ ] `.gitignore` (Step 4.5)
- [ ] `.python-version` (Step 4.5) — overwrite existing `3.14.6` with `3.12` per task spec
- [ ] `.dockerignore` (Step 4.5)
- [ ] `README.md` updated with Quickstart (Step 4.7)
- [ ] N/A — no migrations (ADR-009).
- [ ] N/A — no contract file (CLI-only per ADR-005).
- [ ] N/A — no feature flag entry (single-process CLI, ADR).
- [ ] PR: `task-001: Dev Tooling Bootstrap` linking this plan and the source `task.md`.
- [ ] Update to `docs/monte-carlo-risk/250.epics-tasks/dependency-graph.md`: mark `task-001` `Done`, record actual cycle time.

## 8. Risks & Edge Cases

- **Edge Case BDD expanded — Docker absent:** `make bootstrap` MUST NOT call Docker. Mitigation: the bootstrap recipe installs the package and runs `pytest` only; Docker is touched solely by `make docker-build` and `make docker-smoke`. The recipe detects Docker and prints an informational message; absence is non-fatal. The `tests/test_bootstrap_without_docker.py` test pins this contract by stripping `docker` from `PATH` and re-running the install + pytest subset.
- **Risk — `requires-python` floor vs. local interpreter:** the Sad Path requires the guard to reject Python ≤ 3.11. The repo's current `.python-version` reads `3.14.6`, which satisfies `>=3.12`. Pinning to `3.12` per task spec forces pyenv users to install 3.12 (CI uses `actions/setup-python` with `python-version: "3.12"`, so CI is unaffected). If a developer runs `make bootstrap` with only 3.14 on PATH, the guard's regex check must accept 3.14 as "≥ 3.12" — verify in `scripts/bootstrap_python_guard.sh` with `python -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)"`.
- **Risk — Docker entrypoint fails before task-003 lands:** `python -m monte_carlo_risk` requires `__main__.py`. Step 4.6 adds a placeholder that prints the version; without it, `make docker-smoke` fails. Mitigation already baked into Step 4.6.
- **Risk — pyenv download time blows the 2-minute budget:** the Happy Path budget is 2 min for `make bootstrap` (per scenario). Mitigation: `pip install -e ".[dev]"` from a clean clone with no cache typically finishes in 30–60 s on a developer laptop; the 2-min budget is a hard ceiling. If it overruns, cache wheels via `actions/cache` in CI only — do not add a local wheel cache (defeats the "clean clone" acceptance).
- **Risk — `import-linter` listed in `[dev]` extras but no `.importlinter` contract yet:** listed per task spec; harmless because the tool only runs when a config exists. Confirmed safe.
- **Risk — Out-of-Scope bleed:** strictly NO Typer root, NO hexagonal tree, NO `.importlinter` config, NO `.pre-commit-config.yaml` in this PR. The `[dev]` extras list includes `pre-commit` tooling libraries? — task says "pre-commit hooks are installed" in Scenario 1. To honor that without creating config, the bootstrap recipe skips `pre-commit install` if `.pre-commit-config.yaml` is missing, and prints "pre-commit config not present yet (arrives with task-004)" — keeps Scenario 1 happy without violating Out-of-Scope.
- **Failure mode specific to L1 Infra:** the bootstrap recipe is the on-ramp for every other task; if it is flaky, every downstream task is blocked. Pin all tool versions in `[dev]` extras with `~=` lower bounds to avoid silent breakages.

## 9. Definition of Done

- [ ] All three BDD scenarios satisfied: **Happy Path** (`make bootstrap` exits 0 in < 120 s on a clean clone with Docker installed), **Sad Path** (`make bootstrap` exits non-zero with "Python 3.12 required" on Python ≤ 3.11), **Edge Case — Mandatory** (`make bootstrap` exits 0 with no Docker on host; the "Docker not available" line is printed).
- [ ] All five `Task Breakdown` items ticked with `N/A — <reason>` (API Changes, DB Migrations, Feature Flags, Metrics/Logs, Contract Tests).
- [ ] Tests added: `tests/test_smoke.py`, `tests/test_version.py`, `tests/test_bootstrap_python_guard.py` (Sad Path), `tests/test_bootstrap_without_docker.py` (Edge Case). No Testcontainers needed (L1 with no DB). No Pact needed (no cross-service payload).
- [ ] CI green: lint (`ruff check` + `ruff format --check` + `mypy src`), unit (`pytest -q`). PR ≤ 300 LOC; squash-merged to `main`; branch deleted.
- [ ] Feature flag (N/A) — no flag registered; recorded as N/A.
- [ ] Logs are N/A in this task (structlog wiring is task-025). No `console.log` analog in Python; ensure `print` calls in `__main__.py` are minimal (one line) and replaced by `structlog` in task-025.
- [ ] External HTTP calls: N/A (no network in this task). Timeout + circuit breaker not applicable yet.
- [ ] ORM entity: N/A (no ORM, no domain).

## 10. Anti-Patterns to Avoid

- **ORM Bleed** — N/A (no ORM yet).
- **CI Bottleneck** — keep this PR's CI to `lint` + `pytest` only; Docker build is opt-in via `make docker-build` and arrives as a dedicated job in task-028 (E2E smoke).
- **100% Coverage Vanity** — do NOT add a coverage floor in `pyproject.toml` for this task; the 0% floor in `Makefile` is a placeholder until task-002 introduces domain code worth measuring.
- **Swallowing Exceptions** — the Python-version guard MUST exit non-zero on bad versions; never `|| true`.
- **Full-Stack Single Commit** — this PR is tooling only. Do NOT add the Typer root, the hexagonal tree, the `.importlinter` config, or any CLI commands.
- **Designing in the IDE** — if the `task.md` is ambiguous (e.g. Python version floor vs. pin), stop and ask. Concrete ambiguity already flagged: `.python-version` was `3.14.6`, task says `3.12` — proceed with `3.12` per task spec.
- **Long-Lived Branch** — bootstrap must merge same-day; nothing in this task blocks a rebase.
- **Stacked PRs Across Layers** — task-002 (hexagonal layout) MUST wait for this PR; do not bundle the `src/monte_carlo_risk/domain/` skeleton here.
- **Mocking the Database** — N/A (no DB).
- **Picking Up a Blocked Task** — N/A (first in chain).

## Quick-Reference Summary

### Mission
Ship the dev-time toolchain so a clean `git clone && make bootstrap && make test` exits 0 in ≤ 2 min. Foundation for every later task — without this PR, the entire Tracer Bullet is stuck.

### Key Decisions
- Python ≥ 3.12 (pyproject `requires-python`); `.python-version` pinned to `3.12` per task spec.
- Bootstrap MUST succeed without Docker; Docker is opt-in via `make docker-build`.
- Single `Makefile` target set: `bootstrap`, `test`, `lint`, `format`, `docker-build`, `docker-smoke`.
- `src/monte_carlo_risk/__main__.py` placeholder added so the Docker entrypoint does not crash before task-003 lands.

### Critical Artifacts
- Code: `src/monte_carlo_risk/__init__.py`, `src/monte_carlo_risk/__main__.py`.
- Config: `pyproject.toml`, `Makefile`, `Dockerfile`, `docker-compose.yml`, `.gitignore`, `.python-version`, `.dockerignore`.
- Scripts: `scripts/bootstrap_python_guard.sh`, `scripts/ci_smoke_bootstrap.sh`.
- Tests: `tests/__init__.py`, `tests/test_smoke.py`, `tests/test_version.py`, `tests/test_bootstrap_python_guard.py`, `tests/test_bootstrap_without_docker.py`.
- Docs: `README.md` Quickstart section.
- Repo setup touched: `pyproject.toml`, `Makefile`, `Dockerfile`, `docker-compose.yml`, `.gitignore`, `.python-version`, `.dockerignore`, `README.md`.

### Open Blockers
- None. First task in the chain.

### Next-Phase Handoff
Inputs `400.testing` consumes from this task:
- Approved `plan.md` at this same path.
- BDD AC from `task.md` (Happy / Sad / Edge) — co-located with the source task.
- `pyproject.toml` test entry point (`pytest -q`) and `Makefile` `test` target — wired up here.
- `Dockerfile` + `docker-compose.yml` for the E2E docker-smoke job that lands in task-028.
- `.python-version` (`3.12`) and `requires-python = ">=3.12"` for CI matrix pinning.