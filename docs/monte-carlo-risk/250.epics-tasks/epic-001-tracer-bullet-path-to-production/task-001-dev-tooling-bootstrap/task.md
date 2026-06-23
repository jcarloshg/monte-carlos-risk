# Task 001 — Dev Tooling Bootstrap

**Epic:** epic-001-tracer-bullet-path-to-production
**Layer:** Infra
**Sprint:** 01
**Depends on:** none
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## Context

First task of the Tracer Bullet. Establishes the dev-time toolchain, the Docker image, and the one-command bootstrap so every subsequent task lands on a working machine. Traces to Story 1.1 of the Epic.

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a clean git clone on a Linux machine with Docker installed, When I run `make bootstrap`, Then pyproject is installed in editable mode with `[dev]` extras, pre-commit hooks are installed, and the command exits 0 within 2 minutes.
- [ ] **Scenario 2 (Sad Path):** Given the system Python is 3.11 or earlier, When I run `make bootstrap`, Then the command exits non-zero with a clear message "Python 3.12 required" and does NOT silently install on the wrong version.
- [ ] **Edge Case (Mandatory):** If `docker compose` is unavailable on the host, `make bootstrap` MUST still succeed (linting and tests must run without Docker); the Docker image build is gated behind `make docker-build` and is not required for the bootstrap to pass.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A — no CLI commands exposed yet in this task.
- [ ] **Database Migrations:** N/A — no DB (ADR-009).
- [ ] **Feature Flags:** N/A — no flags needed in v1 (single-process CLI).
- [ ] **Metrics / Logs:** N/A — logging setup is `task-003`.
- [ ] **Contract Tests:** N/A — no contracts exercised yet.

## Out of Scope

- Hexagonal package directory tree (created empty by `task-002`).
- The `.importlinter` config (added by `task-004`).
- The Typer CLI root (added by `task-003`).

## Deliverables

- `pyproject.toml` with `python = ">=3.12"`, `[project.optional-dependencies.dev]` listing `pytest`, `pytest-cov`, `ruff`, `mypy`, `import-linter`, `structlog`, `typer`, `numpy`, `matplotlib`.
- `Dockerfile` (python:3.12-slim base, non-root user, `pip install -e .`, ENTRYPOINT `python -m monte_carlo_risk`).
- `docker-compose.yml` with one service `monte-carlo` building from the local Dockerfile.
- `Makefile` with targets: `bootstrap`, `test`, `lint`, `format`, `docker-build`, `docker-smoke`.
- `.gitignore` excluding `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `output/`, `*.egg-info/`, `.venv/`.
- `.python-version` (pin to 3.12).
- Empty `src/monte_carlo_risk/__init__.py` with `__version__ = "0.1.0"`.
- Empty `tests/__init__.py` plus one passing `tests/test_smoke.py` asserting `True`.
