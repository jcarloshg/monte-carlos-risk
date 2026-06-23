# Plan: task-003 — CLI `describe-mock-data` Stub + Error Envelope + structlog

**Source task:** docs/monte-carlo-risk/250.epics-tasks/epic-001-tracer-bullet-path-to-production/task-003-cli-describe-mock-data-stub/task.md
**Plan file:** docs/monte-carlo-risk/250.epics-tasks/epic-001-tracer-bullet-path-to-production/task-003-cli-describe-mock-data-stub/plan.md
**Layer:** Transport (L3)
**Epic:** epic-001-tracer-bullet-path-to-production
**Sprint:** 01
**Owner:** jcarloshg
**Depends on:** task-002 (shared-kernel-value-objects) — **Done** per `dependency-graph.md` row 14
**Estimated PR scope:** 1 PR, ≈ 300 LOC

## 1. Feature Summary

Task-003 is the third task of the Tracer Bullet — and the **first task that exposes a user-facing surface**. Its purpose is to wire the Typer CLI root, the canonical JSON error envelope, and the structlog setup so that every later bounded context (Portfolio in Epic 002, Simulation in Epic 003, Risk Metrics in Epic 004) has a deterministic, contract-driven entry point. The single shipped command — `describe-mock-data` — is intentionally trivial: it returns a hardcoded JSON stub matching `mock_data_descriptor` (provider=`mock`, version=`0.1.0-stub`, tickers=`[]`, date_range=`{null, null}`, frequency=`daily`). The real bundled CSV corpus is deferred to Epic 003 / task-010; this task proves the **path-to-prod plumbing** (CLI root → JSON envelope → JSON logs → Docker invocation) without depending on any domain logic beyond the four shared-kernel value objects shipped in task-002. Traces to Story 1.2 of Epic 001.

Concretely this task ships the entire L3 Transport surface for the project:

- A Typer **composition root** (`src/monte_carlo_risk/interface/cli/app.py`) with three global flags (`--log-level`, `--log-format`, `--run-id`) and the `--help` smoke-test target.
- A **canonical error envelope** (`src/monte_carlo_risk/interface/errors.py`) — a `CanonicalCliError` dataclass plus an `emit_canonical_error(error_code, message, context, run_id)` function that writes **exactly one** canonical JSON line matching `cli-contract.yaml` §`error_schema` to **stderr** and exits with the documented code.
- A **structlog setup** (`src/monte_carlo_risk/interface/logging.py`) that renders one valid JSON event per line to stderr in non-TTY mode (NFR-6, Edge Case BDD).
- **CLI flag validators** (`src/monte_carlo_risk/interface/cli_contract.py`) matching the `flags` section of `cli-contract.yaml`.
- The **`describe-mock-data` command** (`src/monte_carlo_risk/interface/cli/commands/describe_mock_data.py`) — a hardcoded stub returning the contract-shaped JSON.
- A **contract minor version bump** (`docs/monte-carlo-risk/100.planning/contracts/cli-contract.yaml` v1.0.0 → v1.1.0) adding the new `error_code = "cli_argument_error"` to the `error_schema` enum — required so the Sad Path BDD can emit a code that the contract guarantees exists.
- An update to `src/monte_carlo_risk/__main__.py` to invoke the Typer app (replacing the task-001 `print(__version__)` placeholder).

Strictly no domain logic beyond the four shared-kernel value objects from task-002 (`Ticker`, `Weight`, `Currency`, `RunId`); no L1 data layer (ADR-009 — zero datastores); no L4 defense layer (`.importlinter` arrives with task-004); no L5 delivery (no feature flags per ADR-005 / single-process CLI). The task depends only on task-001 (tooling) and task-002 (value objects), both `Done`.

## 2. Pre-Flight Checks

- [x] **task-002 (shared-kernel-value-objects) is merged to `main`** — confirmed in `docs/monte-carlo-risk/250.epics-tasks/dependency-graph.md` row 14 (`Status: Done`). On-disk evidence: `src/monte_carlo_risk/domain/shared_kernel/{ticker,weight,currency,run_id}.py` exist (verified via `ls` on 2026-06-23). The `RunId` value object is the only one this task depends on (used by `emit_canonical_error` to populate the `run_id` field of every error envelope).
- [x] **task-001 (dev-tooling-bootstrap) is merged to `main`** — confirmed in row 13. `pyproject.toml` already declares `typer~=0.12` and `structlog~=24.4` in `[project.optional-dependencies].dev`; no `pyproject.toml` change is required for this task.
- [x] Frozen design artifacts present:
  - `docs/monte-carlo-risk/100.planning/contracts/cli-contract.yaml` v1.0.0 (the immutable surface contract) — defines `global_flags` (`--log-level`, `--log-format`, `--run-id`), the `describe-mock-data` command, the `mock_data_descriptor` stdout schema, and the `error_schema` enum.
  - `docs/monte-carlo-risk/200.designing/architecture/hexagonal.md` §Concrete Layout — defines `interface/cli/{app.py,commands/}`, `interface/errors.py`, `interface/logging.py`, `interface/cli_contract.py` exactly as this task ships them.
  - `docs/monte-carlo-risk/200.designing/architecture/hexagonal.md` §Linter Contract — defines the forbidden-import graph (`interface/` may import `domain/` + stdlib + third-party; must NOT import `application/`, `infrastructure/`, ORM, `pathlib`, `matplotlib`, etc.). task-004 will encode this as `.importlinter`; this task does a manual import audit (Step 4.8).
  - ADRs 001 (hexagonal), 005 (CLI-only), 006 (modular monolith) — already approved.
- [x] Repo + CI baseline present:
  - `pyproject.toml` — `requires-python = ">=3.12"`, `[dev]` extras already include `typer`, `structlog`, `pytest`, `pytest-cov`, `ruff`, `mypy`, `import-linter` (linter unused until task-004).
  - `Makefile` — `bootstrap` / `test` / `lint` / `format` / `docker-build` / `docker-smoke` targets; `lint` runs `ruff check src tests && ruff format --check src tests && mypy src`; `test` runs `pytest -q --cov=src/monte_carlo_risk --cov-fail-under=0`.
  - `docker-compose.yml` — `monte-carlo` service with `image: monte-carlo-risk:dev`; CLI invocation via `docker compose run --rm monte-carlo <command> [flags]`.
  - `scripts/bootstrap_python_guard.sh` — Python-version guard (≥ 3.12).
- [x] Feature flag service: **N/A** — single-process CLI per ADR-005; no flag service is registered. The source `task.md` §Task Breakdown records `Feature Flags: N/A`. Re-confirmed here: do not introduce `feature-flags.yml` in this task.
- [x] No architectural drift detected — `src/monte_carlo_risk/domain/shared_kernel/` is pure stdlib + `uuid` (verified during task-002's `400.testing` audit); `interface/` does not yet exist so the boundary is unobserved but not violated. This task is the first writer to `interface/` and must keep it that way (Step 4.8 manual pre-flight enforces it).
- [ ] **NOTE (non-blocking):** the `.importlinter` config arrives in task-004. This task does a hand-rolled import audit (Step 4.8) before opening the PR — the same forbidden list, applied to `interface/` instead of `domain/`. Do not add `.importlinter` here; that violates this task's `Out of Scope` and would land a 1,500-LOC single-commit PR stacking tasks 003 and 004.

### Blocker — Implementation Not Built (recorded by `400.testing` on 2026-06-23)

The `400.testing` phase ran on `main` @ `1bfec7d` (`Merge pull request #2 from jcarloshg/task-002-shared-kernel-value-objects`), which is the last commit on `main` and corresponds to **task-002 only**. task-003 has no branch, no PR, no merge, and no code on disk. Evidence:

- `git branch -a` returns only `main`, the orphan remote `origin/task-001-dev-tooling-bootstrap`, the orphan remote `origin/task-002-shared-kernel-value-objects`, and the local `task-001-dev-tooling-bootstrap` and `task-002-shared-kernel-value-objects` (both squashed-merged). **No `task-003-cli-describe-mock-data-stub` branch exists.**
- `git log --all --oneline` shows only the task-001 + task-002 history; no commit, no PR #3, no merge for task-003.
- `docs/monte-carlo-risk/250.epics-tasks/dependency-graph.md` row 15 still has `Status:` **empty** (not `Done`).
- `find src tests -type f` shows only the task-001 + task-002 surface (`__init__.py`, `__main__.py`, `domain/{shared_kernel/{ticker,weight,currency,run_id}.py,…}`, plus the four task-002 test files and the four task-001 test files). **None of the §7 artifacts for this task exist.**
- `ls src/monte_carlo_risk/interface` → directory does not exist (the entire `interface/` package — 7 of the 9 source artifacts — is missing).
- `ls tests/unit/interface` → directory does not exist (all 6 test artifacts missing).
- `docs/monte-carlo-risk/100.planning/contracts/cli-contract.yaml` is **still at v1.0.0** with `Frozen on: 2026-06-23` and does **NOT** contain `cli_argument_error` in the `error_schema.error_code` enum. The contract minor bump (Step 4.1) has not been applied.
- `src/monte_carlo_risk/__main__.py` still contains the task-001 placeholder (`print(__version__)`) and has **NOT** been updated to invoke the Typer app (Step 4.6.c).

Therefore **all 16 §7 artifact rows are BLOCKER — not built**, all three §5 BDD scenarios are **untestable**, and this plan is stamped `NOT ISSUED` below. Per skill rule *"do not run tests against missing code"*, no `pytest`, `ruff`, `mypy`, `pip-audit`, Docker build, or Typer `CliRunner` invocation was performed — there is nothing to test. The plan is returned to the implementer to land the PR described in §4–§6, then re-enter `400.testing`.

| §7 Artifact                      | Path                                                                | On disk?           | Notes                                                  |
| -------------------------------- | ------------------------------------------------------------------- | ------------------ | ------------------------------------------------------ |
| Contract minor bump              | `docs/monte-carlo-risk/100.planning/contracts/cli-contract.yaml`    | ❌ **NOT MODIFIED** | Still at `v1.0.0`; no `cli_argument_error` enum entry. |
| Interface package marker         | `src/monte_carlo_risk/interface/__init__.py`                        | ❌ **NOT BUILT**    | `interface/` directory does not exist.                 |
| CLI sub-package marker           | `src/monte_carlo_risk/interface/cli/__init__.py`                    | ❌ **NOT BUILT**    | —                                                      |
| Commands sub-package marker      | `src/monte_carlo_risk/interface/cli/commands/__init__.py`           | ❌ **NOT BUILT**    | —                                                      |
| Canonical error envelope         | `src/monte_carlo_risk/interface/errors.py`                          | ❌ **NOT BUILT**    | —                                                      |
| structlog configuration          | `src/monte_carlo_risk/interface/logging.py`                         | ❌ **NOT BUILT**    | —                                                      |
| CLI flag validators              | `src/monte_carlo_risk/interface/cli_contract.py`                    | ❌ **NOT BUILT**    | —                                                      |
| `describe-mock-data` command     | `src/monte_carlo_risk/interface/cli/commands/describe_mock_data.py` | ❌ **NOT BUILT**    | —                                                      |
| Typer composition root           | `src/monte_carlo_risk/interface/cli/app.py`                         | ❌ **NOT BUILT**    | —                                                      |
| Modified `__main__.py`           | `src/monte_carlo_risk/__main__.py`                                  | ❌ **NOT MODIFIED** | Still the task-001 placeholder `print(__version__)`.   |
| Interface test marker            | `tests/unit/interface/__init__.py`                                  | ❌ **NOT BUILT**    | `tests/unit/interface/` does not exist.                |
| CLI test sub-package marker      | `tests/unit/interface/cli/__init__.py`                              | ❌ **NOT BUILT**    | —                                                      |
| Commands test sub-package marker | `tests/unit/interface/cli/commands/__init__.py`                     | ❌ **NOT BUILT**    | —                                                      |
| Sad-Path tests                   | `tests/unit/interface/test_canonical_error.py`                      | ❌ **NOT BUILT**    | —                                                      |
| Happy-Path tests                 | `tests/unit/interface/test_describe_mock_data.py`                   | ❌ **NOT BUILT**    | —                                                      |
| Edge-Case tests                  | `tests/unit/interface/test_logging.py`                              | ❌ **NOT BUILT**    | —                                                      |

## 3. Setup

1. Branch off `main`: `task-003-cli-describe-mock-data-stub`.
2. Confirm `make bootstrap` is still green on this branch — `pytest -q` must report the 65 existing tests (10 from task-001 + 55 from task-002) passing.
3. Confirm the Typer + structlog dev dependencies resolve in the current `pip install -e ".[dev]"` environment: `python -c "import typer, structlog; print(typer.__version__, structlog.__version__)"`. If a clean-machine `make bootstrap` succeeds on this branch, both are present and the task ships no `pyproject.toml` diff.
4. No secrets, no feature flags, no external services to pre-register. No DB to migrate (ADR-009 — zero datastores). No external HTTP calls (ADR-005 — CLI-only v1, no `HttpMarketDataSource`).
5. Pre-create the target directory tree (no-op until Step 4.2 lands): `src/monte_carlo_risk/interface/{cli,cli/commands}/`, `tests/unit/interface/`.

## 4. Implementation Steps (Ordered)

> **Layer ordering rationale:** L1 Data/Infra → L2 Domain → L3 Transport → L4 Defense → L5 Delivery. For this task, L1 and L2 have **no new work** (the contract bump in Step 4.1 is the closest analogue to L1; the shared kernel from task-002 already exists). All meaningful work is L3 Transport (Steps 4.2–4.7); L4 Defense is satisfied by a single manual pre-flight (Step 4.8). L5 Delivery is N/A. The contract bump (Step 4.1) lands **first** so the contract is the single source of truth and the code is implemented against v1.1.0 from the start.

### Step 4.1 — Contract minor-version bump (frozen source of truth)

- File(s) to modify: `docs/monte-carlo-risk/100.planning/contracts/cli-contract.yaml`
- What to write:
  - **Version header:** change the top-of-file `# Version: v1.0.0` to `# Version: v1.1.0` and bump `# Frozen on: 2026-06-23` to the date of this PR (whichever date the commit lands — record in the commit body too, per the source `task.md`).
  - **`error_schema.error_code` enum:** add the new value `- cli_argument_error` to the existing list (currently 14 codes, ends at `- invalid_simulation_transition`). Place it **last** in the enum to minimize diff churn and signal "new addition."
  - **`versioning` rules:** no change (adding an enum value is already covered by the existing `minor: v1.N.0 — a new optional field in any schema` rule; explicitly note in the commit body that this is a `minor` bump per that rule).
- Verify:
  - `python -c "import yaml; d=yaml.safe_load(open('docs/monte-carlo-risk/100.planning/contracts/cli-contract.yaml')); assert d['versioning'] is not None or 'versioning' in d; print(d.get('version'), 'OK')"` — or simply `git diff` the file and confirm only the version header + one new enum line changed.
  - Run `ruff format --check docs` (no-op; YAML is not linted by ruff, but confirms the file parses).
  - Update the `versioning` comment block at the bottom of the file to add a one-line changelog entry: `# 2026-06-23 v1.1.0 — added error_code "cli_argument_error" (task-003).` This is the immutable audit trail required by `cli-contract.yaml` §Versioning Rules (`supersession` paragraph).

### Step 4.2 — L3 Transport: scaffold the `interface/` package tree

- File(s) to create:
  - `src/monte_carlo_risk/interface/__init__.py` — empty (package marker; no re-exports).
  - `src/monte_carlo_risk/interface/cli/__init__.py` — empty (sub-package marker).
  - `src/monte_carlo_risk/interface/cli/commands/__init__.py` — empty (sub-package marker).
  - `tests/unit/interface/__init__.py` — empty (test package marker mirroring `src/`).
  - `tests/unit/interface/cli/__init__.py` — empty (mirrors `src/monte_carlo_risk/interface/cli/`).
  - `tests/unit/interface/cli/commands/__init__.py` — empty (mirrors `src/monte_carlo_risk/interface/cli/commands/`).
- What to write: pure package-marker files. No code, no re-exports.
- Verify: `python -c "from monte_carlo_risk.interface import cli"` resolves without `ModuleNotFoundError`. `pytest --collect-only -q` does not error on the new test root.

### Step 4.3 — L3 Transport: implement `interface/errors.py` (canonical error envelope)

- File(s) to create: `src/monte_carlo_risk/interface/errors.py`
- What to write:
  - `@dataclass(frozen=True) class CanonicalCliError:` — fields:
    - `error_code: str` — must be one of the enum values in `cli-contract.yaml` §`error_schema.error_code` (validated at construction against the YAML-loaded enum set; raise `ValueError` if a code is not in the contract, so a typo like `"cli_argument_erorr"` fails loud and fast).
    - `message: str` — human-readable explanation (free-form text; never includes secrets).
    - `context: dict[str, object] | None = None` — structured debug context; never includes secrets (per the contract's `context` description).
    - `run_id: RunId` — uses the `RunId` value object shipped in task-002 (do NOT use raw `uuid.UUID`; the boundary must be type-enforced at the CLI layer).
  - `def emit_canonical_error(error: CanonicalCliError) -> None:` — writes **exactly one** canonical JSON line to **stderr** using `print(json.dumps(payload, sort_keys=True), file=sys.stderr)` where `payload` matches `cli-contract.yaml` §`error_schema` (keys `error_code`, `message`, `context` (omitted if `None`), `run_id` (as the UUID4 string from `str(error.run_id.value)`)). Exits via `sys.exit(<exit_code_for_error_code>)` — exit codes are looked up from a module-level constant table that maps each known `error_code` to its documented exit code (the contract defines exit codes per-command, not per-error; this task uses exit `2` for `cli_argument_error` matching the `simulate` command's documented `2: input validation failure`).
  - Module-level constants:
    - `_EXIT_CODE_BY_ERROR_CODE: dict[str, int] = {"cli_argument_error": 2, ...}` — start with only `cli_argument_error` (the only error code this task emits). Future tasks add entries as they introduce new codes. **Do not** pre-populate this table with exit codes for codes this task does not emit — that is scope bleed.
  - Imports: `from __future__ import annotations`, `import json`, `import sys`, `from dataclasses import dataclass`, `from monte_carlo_risk.domain.shared_kernel import RunId`. No other imports — particularly no `typer`, no `click`, no `pathlib`.
- Verify:
  - Import in a Python REPL: `from monte_carlo_risk.interface.errors import CanonicalCliError, emit_canonical_error; from monte_carlo_risk.domain.shared_kernel import RunId; e = CanonicalCliError(error_code="cli_argument_error", message="unknown flag: --bogus", run_id=RunId()); print(e)` — constructs without error.
  - `ruff check src/monte_carlo_risk/interface/errors.py && ruff format --check src/monte_carlo_risk/interface/errors.py && mypy src/monte_carlo_risk/interface/errors.py` exit 0.

### Step 4.4 — L3 Transport: implement `interface/logging.py` (structlog setup)

- File(s) to create: `src/monte_carlo_risk/interface/logging.py`
- What to write:
  - `def configure_logging(*, log_level: str = "INFO", log_format: str = "json", stream: TextIO | None = None) -> None:` — configures structlog globally (idempotent; safe to call multiple times — uses `structlog.reset_defaults()` then `structlog.configure(...)`). Behaviour:
    - `log_level` ∈ `{DEBUG, INFO, WARNING, ERROR}` per `cli-contract.yaml` §`global_flags.--log-level`. Map to `structlog.stdlib.NAME_TO_LEVEL` (or use `structlog.make_filtering_bound_logger` for non-stdlib config).
    - `log_format == "json"`: use `structlog.processors.JSONRenderer(sort_keys=True)` so every event is a single valid JSON line (drives the **Edge Case BDD**).
    - `log_format == "text"`: use `structlog.dev.ConsoleRenderer` with `colors=False` when `stream.isatty()` is `False` (i.e. CI / non-TTY) so output is parseable by humans **and** machines, and `colors=True` when `stream.isatty()` is `True`. **Always** force `colors=False` when `stream.isatty()` is `False` — this is the load-bearing line for the Edge Case BDD.
    - Processors chain (in order): `structlog.contextvars.merge_contextvars`, `structlog.processors.add_log_level`, `structlog.processors.TimeStamper(fmt="iso")`, `structlog.processors.StackInfoRenderer()`, `structlog.processors.format_exc_info`, `structlog.processors.dict_tracebacks` (last processor = the renderer chosen above). The `format_exc_info` + `dict_tracebacks` combo ensures tracebacks serialize to single-line JSON (no multi-line stack traces in stderr — directly satisfies Edge Case BDD).
    - `stream` defaults to `sys.stderr` when `None`.
  - Module-level constant `DEFAULT_LOGGING = {"log_level": "INFO", "log_format": "json"}` matching the contract defaults.
  - Imports: `from __future__ import annotations`, `import sys`, `from typing import TextIO`, `import structlog`. No `typer`, no `click`, no `pathlib`, no `domain.` imports — logging is purely a transport concern.
- Verify:
  - `python -c "from monte_carlo_risk.interface.logging import configure_logging; configure_logging(log_format='json'); import structlog; log = structlog.get_logger(); log.info('hello', foo=42); log.warning('something', path='/tmp/x')"` — emits two single-line JSON objects to stderr.
  - `ruff check src/monte_carlo_risk/interface/logging.py && ruff format --check src/monte_carlo_risk/interface/logging.py && mypy src/monte_carlo_risk/interface/logging.py` exit 0.

### Step 4.5 — L3 Transport: implement `interface/cli_contract.py` (flag validators)

- File(s) to create: `src/monte_carlo_risk/interface/cli_contract.py`
- What to write:
  - `LOG_LEVELS: frozenset[str] = frozenset({"DEBUG", "INFO", "WARNING", "ERROR"})` — mirrors the contract enum.
  - `LOG_FORMATS: frozenset[str] = frozenset({"json", "text"})` — mirrors the contract enum.
  - `def validate_log_level(value: str) -> str:` — returns `value` if in `LOG_LEVELS`, else raises a typed `InvalidLogLevelError(ValueError)` with the canonical message.
  - `def validate_log_format(value: str) -> str:` — same shape, for `LOG_FORMATS`.
  - `def parse_run_id(value: str) -> RunId:` — if `value == "auto"` (the contract default), return `RunId()` (fresh UUID4); else try `RunId(value)` and let `InvalidRunIdError` propagate on bad input. **No** silent fallback — bad input is a user error and must surface as a `cli_argument_error`.
  - `class InvalidLogLevelError(ValueError)` and `class InvalidLogFormatError(ValueError)` — typed exceptions, mirroring the `InvalidTickerError` style from task-002.
  - Imports: `from __future__ import annotations`, `from monte_carlo_risk.domain.shared_kernel import RunId`. No `typer`, no `click`, no `pathlib` — this module is a pure-Python validator library, **independently** of Typer so it can be unit-tested without spinning up a CLI runner.
- Verify:
  - `python -c "from monte_carlo_risk.interface.cli_contract import validate_log_level, validate_log_format, parse_run_id; assert validate_log_level('DEBUG') == 'DEBUG'; assert validate_log_format('json') == 'json'; assert parse_run_id('auto').value.version == 4"` — passes.
  - `python -c "from monte_carlo_risk.interface.cli_contract import validate_log_level; validate_log_level('TRACE')"` — raises `InvalidLogLevelError`.
  - `ruff check src/monte_carlo_risk/interface/cli_contract.py && ruff format --check src/monte_carlo_risk/interface/cli_contract.py && mypy src/monte_carlo_risk/interface/cli_contract.py` exit 0.

### Step 4.6 — L3 Transport: implement `interface/cli/commands/describe_mock_data.py` + `interface/cli/app.py` + update `__main__.py`

This is the biggest step; split into three sub-steps for reviewability.

#### Step 4.6.a — `commands/describe_mock_data.py`

- File(s) to create: `src/monte_carlo_risk/interface/cli/commands/describe_mock_data.py`
- What to write:
  - Module-level constant `MOCK_DATA_DESCRIPTOR_STUB: dict[str, object] = {"provider": "mock", "version": "0.1.0-stub", "tickers": [], "date_range": {"start": None, "end": None}, "frequency": "daily"}` — exact shape required by `cli-contract.yaml` §`mock_data_descriptor` and by the Happy Path BDD.
  - `def describe_mock_data() -> None:` — emits the stub as **one valid JSON line** to **stdout** via `print(json.dumps(MOCK_DATA_DESCRIPTOR_STUB, sort_keys=True))`. Returns normally (exit code 0 by default). No flags, no arguments (the `describe-mock-data` command in `cli-contract.yaml` has `flags: []`). No logging in this task — the BDD does not require it, and logging lands in task-025 (structlog event wiring).
  - Imports: `from __future__ import annotations`, `import json`. No `typer` import at the function level — Typer decoration lives in `app.py` (composition root). This keeps `describe_mock_data()` unit-testable as a plain Python function (Step 4.7).
- Verify:
  - `python -c "from monte_carlo_risk.interface.cli.commands.describe_mock_data import describe_mock_data, MOCK_DATA_DESCRIPTOR_STUB; import json; assert MOCK_DATA_DESCRIPTOR_STUB == json.loads(json.dumps(MOCK_DATA_DESCRIPTOR_STUB))"` — round-trips.
  - `ruff check src/monte_carlo_risk/interface/cli/commands/describe_mock_data.py && ruff format --check src/monte_carlo_risk/interface/cli/commands/describe_mock_data.py && mypy src/monte_carlo_risk/interface/cli/commands/describe_mock_data.py` exit 0.

#### Step 4.6.b — `cli/app.py` (Typer root + global flag callbacks)

- File(s) to create: `src/monte_carlo_risk/interface/cli/app.py`
- What to write:
  - `app: typer.Typer = typer.Typer(name="monte-carlo", no_args_is_help=True, add_completion=False)` — the composition root.
  - Three **global flag callbacks** registered via `app.callback()`:
    - `--log-level` callback → calls `configure_logging(log_level=validate_log_level(value))` (Step 4.4 + Step 4.5). Wraps any `InvalidLogLevelError` in `CanonicalCliError(error_code="cli_argument_error", message=str(exc), context={"flag": "--log-level", "value": value}, run_id=...)` and emits via `emit_canonical_error(...)` — exit code 2.
    - `--log-format` callback → same pattern with `validate_log_format` and `context={"flag": "--log-format", "value": value}`.
    - `--run-id` callback → stores the parsed `RunId` in a module-level `_current_run_id: RunId = RunId()` (sentinel default; `parse_run_id("auto")` replaces it). The canonical error envelope reads `_current_run_id` so every emitted error line carries the same `--run-id` (NFR-6 / Edge Case BDD).
  - One **sub-command** registration:
    - `app.command(name="describe-mock-data")(describe_mock_data)` — wires the Step 4.6.a function to the Typer CLI. Typer will validate that there are no positional args or unknown flags; an unknown flag like `--bogus` triggers Typer's built-in `BadParameter` (a subclass of `click.exceptions.UsageError`), which this step must catch and convert to the canonical envelope.
  - **Unknown-flag catch-all:** wrap the entire `app()` invocation (in `__main__.py`, Step 4.6.c) with a `try: app() except (typer.BadParameter, click.exceptions.UsageError) as exc: emit_canonical_error(CanonicalCliError(error_code="cli_argument_error", message=str(exc), context={"argv": sys.argv[1:]}, run_id=_current_run_id)); sys.exit(2)`. This satisfies the Sad Path BDD (`--bogus` → exit 2 + canonical JSON error line).
  - `--help` smoke-test target: Typer auto-generates `--help` for `app` and for each subcommand — no code needed; the `describe_mock_data` Typer wrapper around the plain-Python function (Step 4.6.a) gets `--help` for free.
  - Imports: `from __future__ import annotations`, `import sys`, `import typer`, `import click`, `from monte_carlo_risk.interface.errors import CanonicalCliError, emit_canonical_error`, `from monte_carlo_risk.interface.logging import configure_logging`, `from monte_carlo_risk.interface.cli_contract import validate_log_level, validate_log_format, parse_run_id`, `from monte_carlo_risk.domain.shared_kernel import RunId`, `from monte_carlo_risk.interface.cli.commands.describe_mock_data import describe_mock_data`. **Boundary check:** imports from `domain.shared_kernel` ✅ (allowed by ADR-001/007); imports from `interface.*` and stdlib ✅; **no** imports from `application.*` or `infrastructure.*` (verified by Step 4.8 audit).
- Verify:
  - `python -m monte_carlo_risk --help` → prints help text containing `describe-mock-data`; exit 0.
  - `python -m monte_carlo_risk describe-mock-data --help` → prints help text for the sub-command; exit 0.
  - `python -m monte_carlo_risk describe-mock-data` → exit 0, stdout is the stub JSON line.
  - `python -m monte_carlo_risk describe-mock-data --bogus` → exit 2, stderr contains exactly one canonical JSON error line with `error_code == "cli_argument_error"` (and a `run_id` matching the auto-generated UUID4).
  - `ruff check src/monte_carlo_risk/interface/cli/app.py && ruff format --check src/monte_carlo_risk/interface/cli/app.py && mypy src/monte_carlo_risk/interface/cli/app.py` exit 0.

#### Step 4.6.c — update `src/monte_carlo_risk/__main__.py`

- File(s) to modify: `src/monte_carlo_risk/__main__.py`
- What to write:
  - Replace the task-001 placeholder (`print(__version__)`) with: `from monte_carlo_risk.interface.cli.app import app; if __name__ == "__main__": app()`. Typer handles exit codes; the unknown-flag catch-all from Step 4.6.b ensures exit code 2 for invalid flags.
- Verify:
  - `python -m monte_carlo_risk describe-mock-data` → exit 0, stdout JSON; same as Step 4.6.b's verify entry, but now invoked via `python -m monte_carlo_risk` (the contract's `invocation_modes[0]`).
  - `python -m monte_carlo_risk describe-mock-data --bogus` → exit 2, stderr canonical error line.

### Step 4.7 — L3 Transport: tests for Happy / Sad / Edge BDD scenarios

Three test files; one per BDD scenario. The first two are exactly the deliverables listed in the source `task.md`; the third (`test_logging.py`) is **added by this plan** to satisfy the mandatory Edge Case BDD (the source `task.md` does not name a file for the Edge Case test). The deviation is documented here and in §7.

#### Step 4.7.a — `tests/unit/interface/test_canonical_error.py` (Sad Path BDD)

- File(s) to create: `tests/unit/interface/test_canonical_error.py`
- What to write (pytest, `typer.testing.CliRunner`):
  - `test_emit_canonical_error_writes_one_json_line_to_stderr` — instantiate `CanonicalCliError(error_code="cli_argument_error", message="unknown flag: --bogus", context={"flag": "--bogus"}, run_id=RunId())`, redirect stderr to `io.StringIO()`, call `emit_canonical_error(error)`, parse the captured stderr as JSON via `json.loads`, assert: keys are exactly `{"error_code", "message", "context", "run_id"}`; `error_code == "cli_argument_error"`; `message == "unknown flag: --bogus"`; `context == {"flag": "--bogus"}`; `run_id` is a valid UUID4 string.
  - `test_emit_canonical_error_emits_exactly_one_line` — invoke `emit_canonical_error` twice in sequence; assert stderr captures exactly two lines (each its own JSON object); confirm `\n` is the only separator (no multi-line JSON, no `\\n` escapes inside a value).
  - `test_emit_canonical_error_rejects_unknown_error_code` — instantiate `CanonicalCliError(error_code="not_a_real_code", message="x", run_id=RunId())`; assert `ValueError` is raised (the construction-time contract check from Step 4.3).
  - `test_unknown_flag_emits_canonical_error_with_exit_code_2` (Typer-level integration) — use `CliRunner(mix_stderr=False)`, invoke `["describe-mock-data", "--bogus"]`, assert `result.exit_code == 2`, assert `json.loads(result.stderr.splitlines()[0])["error_code"] == "cli_argument_error"`, assert `len(result.stderr.splitlines()) == 1` (exactly one canonical error line).
  - **Sad Path BDD coverage:** the fourth test asserts the contract end-to-end (CLI invocation → canonical error envelope → exit code 2) — this is the test that satisfies Scenario 2 of the source `task.md`.
- Imports: `from __future__ import annotations`, `import io`, `import json`, `import pytest`, `from typer.testing import CliRunner`, `from monte_carlo_risk.interface.cli.app import app`, `from monte_carlo_risk.interface.errors import CanonicalCliError, emit_canonical_error`, `from monte_carlo_risk.domain.shared_kernel import RunId`.
- Verify: `pytest tests/unit/interface/test_canonical_error.py -q` exits 0; all four tests pass.

#### Step 4.7.b — `tests/unit/interface/test_describe_mock_data.py` (Happy Path BDD)

- File(s) to create: `tests/unit/interface/test_describe_mock_data.py`
- What to write (pytest, `typer.testing.CliRunner`):
  - `test_describe_mock_data_returns_stub_matching_contract` — use `CliRunner(mix_stderr=False)`, invoke `["describe-mock-data"]`, assert `result.exit_code == 0`, assert the single stdout line parses as JSON and equals the `MOCK_DATA_DESCRIPTOR_STUB` dict byte-for-byte (compare dicts, not strings, to avoid whitespace noise).
  - `test_describe_mock_data_stub_has_required_keys` — defensive: assert the stub contains exactly the five required keys `{"provider", "version", "tickers", "date_range", "frequency"}` (per `cli-contract.yaml` §`mock_data_descriptor.required`); assert `provider == "mock"` and `version == "0.1.0-stub"` per the Happy Path BDD.
  - `test_describe_mock_data_emits_exactly_one_stdout_line` — invoke via `CliRunner`; assert `len(result.stdout.splitlines()) == 1`.
  - **Happy Path BDD coverage:** the first test asserts the contract end-to-end (CLI invocation → JSON stub matching `mock_data_descriptor` → exit 0) — this is the test that satisfies Scenario 1 of the source `task.md`.
- Imports: `from __future__ import annotations`, `import json`, `import pytest`, `from typer.testing import CliRunner`, `from monte_carlo_risk.interface.cli.app import app`, `from monte_carlo_risk.interface.cli.commands.describe_mock_data import MOCK_DATA_DESCRIPTOR_STUB`.
- Verify: `pytest tests/unit/interface/test_describe_mock_data.py -q` exits 0; all three tests pass.

#### Step 4.7.c — `tests/unit/interface/test_logging.py` (Edge Case BDD — added by this plan)

- File(s) to create: `tests/unit/interface/test_logging.py` (**scope addition** — see §7)
- What to write (pytest, no CLI runner needed; pure unit on `configure_logging`):
  - `test_structlog_json_renderer_emits_one_valid_json_per_line_in_non_tty` — call `configure_logging(log_format="json", stream=io.StringIO())` (explicit `StringIO` simulates the non-TTY case; `isatty()` returns `False`), emit three events with `structlog.get_logger().info("evt1", k=1)`, `.warning("evt2", k=2)`, `.error("evt3", k=3)`, then assert: each captured line parses as a valid JSON object via `json.loads`; no line contains a literal `\n` inside the JSON value (i.e. no multi-line stack traces); the three JSON objects have `event` fields `"evt1"`, `"evt2"`, `"evt3"` respectively, and the log level fields `"info"`, `"warning"`, `"error"`.
  - `test_structlog_text_renderer_in_non_tty_disables_colors` — call `configure_logging(log_format="text", stream=io.StringIO())`, emit one event with `structlog.get_logger().info("evt", k=1)`, assert the captured output does NOT contain ANSI escape sequences (regex `r"\x1b\[[0-9;]*m"`).
  - `test_structlog_json_format_includes_iso_timestamp_and_log_level` — emit one event, assert the parsed JSON has keys `timestamp` (parses as ISO-8601 datetime), `level` (one of `debug|info|warning|error`), `event`.
  - **Edge Case BDD coverage:** the first test asserts the contract end-to-end (structlog JSON config + non-TTY stream → one valid JSON per line) — this is the test that satisfies Scenario 3 of the source `task.md`. The second and third are defensive companion tests; the first is the load-bearing one.
- Imports: `from __future__ import annotations`, `import io`, `import json`, `import re`, `import pytest`, `import structlog`, `from datetime import datetime`, `from monte_carlo_risk.interface.logging import configure_logging`.
- Verify: `pytest tests/unit/interface/test_logging.py -q` exits 0; all three tests pass.

#### Step 4.7.d — full suite + non-functional gates

- Verify:
  - `pytest tests/unit/interface -q` exits 0 (covers the three new test files).
  - `pytest -q` exits 0 (full suite: 10 task-001 + 55 task-002 + 10 task-003 = 75 tests).
  - `make lint` exits 0 (`ruff check` + `ruff format --check` + `mypy src`).
  - Total wall-clock of new tests ≤ 2 s (NFR-2: full unit suite ≤ 5 s).

### Step 4.8 — L4 Defense (manual pre-flight ahead of task-004)

- File(s) read (no new files): every file under `src/monte_carlo_risk/interface/`.
- What to write (note, not code): before opening the PR, run an import audit mirroring Step 4.4 of the task-002 plan but scoped to `interface/`:
  - Forbidden (per ADR-001 / `hexagonal.md` §Linter Contract): `matplotlib`, `mpl_toolkits`, `pandas`, `requests`, `httpx`, `urllib3`, `aiohttp`, `sqlalchemy`, `django`, `flask_sqlalchemy`, `peewee`, `tortoise`, `piccolo`, `prisma`, `pathlib` (in `interface/cli/`), `monte_carlo_risk.application`, `monte_carlo_risk.infrastructure`.
  - Allowed: `__future__`, `dataclasses`, `io`, `json`, `re`, `sys`, `typing` (incl. `TextIO`), `click` (Typer dep), `typer`, `structlog`, `monte_carlo_risk.domain.shared_kernel` (`RunId` only — confirmed by reading each import line).
- Verify: every `interface/` file passes the audit; no forbidden imports. If a forbidden import is found, fix it before opening the PR — never let task-004's linter catch it later. (Concrete check: `python -c "import ast, pathlib; [print(p.name, sorted({(n.module if isinstance(n, ast.Import) else (n.module or '') + ('.' + n.name if hasattr(n,'name') and n.name else '')) for n in ast.walk(ast.parse(p.read_text())) if isinstance(n, (ast.Import, ast.ImportFrom))})) for p in pathlib.Path('src/monte_carlo_risk/interface').rglob('*.py')]"`.)

## 5. Testing Strategy

For each BDD scenario in the source `task.md`, name the test file, the test function, and the assertion target.

- [ ] **Happy Path** (`Given the CLI is installed, When I run monte-carlo describe-mock-data, Then exit code is 0 and stdout is a JSON document matching mock_data_descriptor schema (provider: "mock", version: "0.1.0-stub", tickers: [], date_range: {start: null, end: null}, frequency: "daily")`):
  - Test file: `tests/unit/interface/test_describe_mock_data.py`
  - Function: `test_describe_mock_data_returns_stub_matching_contract` (companion tests: `test_describe_mock_data_stub_has_required_keys`, `test_describe_mock_data_emits_exactly_one_stdout_line`).
  - Asserts: `CliRunner().invoke(app, ["describe-mock-data"]).exit_code == 0`; `json.loads(result.stdout)` deeply equals `MOCK_DATA_DESCRIPTOR_STUB` (`{"provider": "mock", "version": "0.1.0-stub", "tickers": [], "date_range": {"start": None, "end": None}, "frequency": "daily"}`); required keys present; stdout is exactly one line.
- [ ] **Sad Path** (`Given the user passes an unknown flag --bogus, When I run monte-carlo describe-mock-data --bogus, Then exit code is 2 and stderr contains exactly one canonical JSON error line matching error_schema with error_code = "cli_argument_error"`):
  - Test file: `tests/unit/interface/test_canonical_error.py`
  - Function: `test_unknown_flag_emits_canonical_error_with_exit_code_2` (companion tests: `test_emit_canonical_error_writes_one_json_line_to_stderr`, `test_emit_canonical_error_emits_exactly_one_line`, `test_emit_canonical_error_rejects_unknown_error_code`).
  - Asserts: `CliRunner(mix_stderr=False).invoke(app, ["describe-mock-data", "--bogus"]).exit_code == 2`; the first (and only) line of stderr parses as JSON with keys `{"error_code", "message", "context", "run_id"}` (or `{"error_code", "message", "run_id"}` if `context` is `None`); `error_code == "cli_argument_error"`; `run_id` is a valid UUID4 string; `len(result.stderr.splitlines()) == 1`.
- [ ] **Edge Case — MANDATORY** (`If structlog is configured for JSON output and the user's terminal is non-TTY (e.g., CI), every event emitted to stderr must be valid JSON on a single line — no multi-line stack traces or colored output. A unit test asserts this by capturing stderr and parsing each line as JSON.`):
  - Test file: `tests/unit/interface/test_logging.py` (**added by this plan** to satisfy the Edge Case BDD; not listed in the source `task.md` deliverables — deviation recorded in §7).
  - Function: `test_structlog_json_renderer_emits_one_valid_json_per_line_in_non_tty` (companion tests: `test_structlog_text_renderer_in_non_tty_disables_colors`, `test_structlog_json_format_includes_iso_timestamp_and_log_level`).
  - Asserts: `configure_logging(log_format="json", stream=io.StringIO())` (non-TTY by construction); three emitted events produce three captured lines; `json.loads(line)` succeeds for each line; no line contains a literal `\n`; the JSON objects contain `event` fields matching the emitted names; the `level` fields match `info`/`warning`/`error`.

Test types per layer:
- L1 → N/A (no DB/cache/broker; ADR-009 — zero datastores).
- L2 → N/A (no new domain code; `RunId` was tested in task-002).
- L3 → **Typer `CliRunner` integration** for the CLI surface (commands + global flags + error envelope) **plus** **pure unit** on `configure_logging` and `emit_canonical_error` (no Typer runner needed). No Pact needed (no cross-service payload — this is a CLI, not an HTTP server). No supertest needed (no HTTP).
- L4 → N/A (`import-linter` arrives with task-004; this task substitutes Step 4.8's manual import audit).
- L5 → N/A (no feature flag, no runbook drill, no canary).

## 6. PR + Merge

1. PR title: `task-003: CLI describe-mock-data Stub + Error Envelope + structlog`.
2. PR description:
   - Link the source task: `docs/monte-carlo-risk/250.epics-tasks/epic-001-tracer-bullet-path-to-production/task-003-cli-describe-mock-data-stub/task.md`.
   - Copy the three BDD scenarios (Happy / Sad / Edge) as the PR checklist.
   - Tick each `Task Breakdown` item as it lands:
     - API Changes: ✅ — adds `describe-mock-data` CLI command (contract v1.1.0; was already declared in v1.0.0 with no flags; new `cli_argument_error` enum value added).
     - DB Migrations: N/A — no DB (ADR-009).
     - Feature Flags: N/A — single-process CLI per ADR-005.
     - Metrics / Logs: ✅ — adds structlog configuration (`src/monte_carlo_risk/interface/logging.py`).
     - Contract Tests: N/A — first contract test lands with Epic 002 / task-009.
   - Explicitly call out the **§7 deviation**: `tests/unit/interface/test_logging.py` is added by this plan (not in the source `task.md` deliverables) to satisfy the mandatory Edge Case BDD. Reviewer can either accept the addition or request it be split into a follow-up PR.
3. Cap PR at ≈ 300 LOC (per task spec); if larger, split into stacked branches (e.g. `errors.py + logging.py + cli_contract.py` first, then `commands/describe_mock_data.py + app.py + __main__.py` + tests). The proposed implementation totals ~280 LOC source + ~120 LOC tests = ~400 LOC across 12 files — over the cap by ~100 LOC. **Recommended split:** PR-A (`errors.py`, `logging.py`, `cli_contract.py`, the contract bump, and their unit tests) + PR-B (`describe_mock_data.py`, `app.py`, `__main__.py` update, the CliRunner tests). PR-B depends on PR-A. If reviewer prefers a single PR, accept the deviation and document it in the PR description.
4. CI must be green:
   - `make bootstrap` (Python-version guard passes; existing 65 tests still pass).
   - `make lint` (`ruff check` + `ruff format --check` + `mypy src`).
   - `make test` (`pytest -q --cov=src/monte_carlo_risk --cov-fail-under=0` — task-003's coverage should be > 80 % on `interface/errors.py` and `interface/logging.py`; > 70 % on `interface/cli_contract.py`).
   - `make docker-build && make docker-smoke` (verifies `docker compose run --rm monte-carlo python -c "import monte_carlo_risk; print(monte_carlo_risk.__version__)"` still works, and the new `docker compose run --rm monte-carlo describe-mock-data` exits 0 with the stub JSON).
   - The `domain-purity` / `import-linter` job arrives with task-004 — explicitly not gated on this PR; manual pre-flight (Step 4.8) substitutes for it.
5. Reviewer focus:
   - BDD AC satisfaction (Happy / Sad / Edge).
   - Out-of-Scope adherence: no `simulate` command (Epic 003), no `validate-portfolio` command (Epic 002), no real mock CSV corpus (Epic 003 / task-010), no actual event emission from the orchestrator (Epic 006 / task-025). All five of those are explicitly called out in the source `task.md` §Out of Scope.
   - Diff size: ≤ 300 LOC if single PR; ≤ 200 LOC per stacked PR.
   - Architecture: `interface/` may import from `domain.shared_kernel` (for `RunId`) and from third-party libs (`typer`, `structlog`, `click`); must NOT import from `application/`, `infrastructure/`, ORM, `matplotlib`, `pandas`, `requests`, `pathlib` (in `cli/`). Step 4.8's manual audit is the gate; reviewer can spot-check the import lines.
6. Merge: **squash-merge to `main`**, delete the branch, mark `task-003` `Done` in `docs/monte-carlo-risk/250.epics-tasks/dependency-graph.md`, record actual cycle time.

## 7. Artifacts to Produce

- [ ] `docs/monte-carlo-risk/100.planning/contracts/cli-contract.yaml` — bumped v1.0.0 → v1.1.0 with `cli_argument_error` added to `error_schema` enum (Step 4.1).
- [ ] `src/monte_carlo_risk/interface/__init__.py` — package marker (Step 4.2).
- [ ] `src/monte_carlo_risk/interface/cli/__init__.py` — sub-package marker (Step 4.2).
- [ ] `src/monte_carlo_risk/interface/cli/commands/__init__.py` — sub-package marker (Step 4.2).
- [ ] `src/monte_carlo_risk/interface/errors.py` — `CanonicalCliError` + `emit_canonical_error` + `_EXIT_CODE_BY_ERROR_CODE` (Step 4.3).
- [ ] `src/monte_carlo_risk/interface/logging.py` — `configure_logging` + `DEFAULT_LOGGING` (Step 4.4).
- [ ] `src/monte_carlo_risk/interface/cli_contract.py` — flag validators + typed exceptions (Step 4.5).
- [ ] `src/monte_carlo_risk/interface/cli/commands/describe_mock_data.py` — stub command + `MOCK_DATA_DESCRIPTOR_STUB` (Step 4.6.a).
- [ ] `src/monte_carlo_risk/interface/cli/app.py` — Typer root + global flag callbacks + unknown-flag catch-all (Step 4.6.b).
- [ ] `src/monte_carlo_risk/__main__.py` — modified to invoke `app()` (Step 4.6.c).
- [ ] `tests/unit/interface/__init__.py` — test package marker (Step 4.2).
- [ ] `tests/unit/interface/cli/__init__.py` — test sub-package marker (Step 4.2).
- [ ] `tests/unit/interface/cli/commands/__init__.py` — test sub-package marker (Step 4.2).
- [ ] `tests/unit/interface/test_canonical_error.py` — Sad Path BDD coverage (Step 4.7.a).
- [ ] `tests/unit/interface/test_describe_mock_data.py` — Happy Path BDD coverage (Step 4.7.b).
- [ ] `tests/unit/interface/test_logging.py` — Edge Case BDD coverage (Step 4.7.c). **Deviation:** this file is **added by this plan**, not listed in the source `task.md` §Deliverables. Reason: the Edge Case BDD requires a unit test that captures stderr and parses each line as JSON, but the source task.md names only two test files (`test_canonical_error.py`, `test_describe_mock_data.py`). A third test file dedicated to `configure_logging` is the cleanest placement (separation of concerns; future logging tests in task-025 / task-026 will live alongside it). Acceptable alternatives: (a) embed the Edge Case test inside `test_canonical_error.py` (smaller diff, but conflates error-envelope and logging concerns); (b) defer the Edge Case test to task-025 (creates a gap where task-003 ships without Edge Case coverage). This plan recommends (c) ship `test_logging.py` now. Reviewer can override.
- [ ] N/A — no migration file (ADR-009 — zero datastores).
- [ ] N/A — no new transport contract file (the surface contract lives at `docs/monte-carlo-risk/100.planning/contracts/cli-contract.yaml`; the v1.1.0 bump in Step 4.1 is a modification, not a new file).
- [ ] N/A — no feature flag entry (single-process CLI per ADR-005).
- [ ] PR: `task-003: CLI describe-mock-data Stub + Error Envelope + structlog` linking this plan and the source `task.md`.
- [ ] Update to `docs/monte-carlo-risk/250.epics-tasks/dependency-graph.md`: mark `task-003` `Done`, record actual cycle time. This unblocks `task-004` (import-linter-and-ci-pipeline).

## 8. Risks & Edge Cases

- **Edge Case BDD expanded — single-line JSON on non-TTY stderr.** The contract says "every event emitted to stderr must be valid JSON on a single line — no multi-line stack traces or colored output." Mitigation: Step 4.4's `structlog` processor chain MUST end with `JSONRenderer(sort_keys=True)` AND must include `dict_tracebacks` (not `traceback.format_tb` or `format_exc_info` alone) so exception traces collapse to single-line structured fields. Drift risk: a future refactor that swaps `dict_tracebacks` for `ConsoleRenderer` would silently break this contract. The `test_structlog_json_renderer_emits_one_valid_json_per_line_in_non_tty` test (Step 4.7.c) is the load-bearing regression test — assert that the test emits three events of mixed level (`info`/`warning`/`error`) and asserts each line parses cleanly. Companion assertion: no line contains a literal `\n` (the test's regex check).
- **Risk — Typer's default error message bypasses the canonical envelope.** Typer / Click have their own error-rendering path (`click.exceptions.UsageError` → "Usage: ..." prefix). If the `app()` invocation in `__main__.py` is not wrapped in a `try/except (typer.BadParameter, click.exceptions.UsageError)`, the Sad Path BDD will produce Typer's text error on stderr instead of the canonical JSON. Mitigation: Step 4.6.b's "Unknown-flag catch-all" wraps `app()` so any Typer/Click error is converted to `CanonicalCliError(error_code="cli_argument_error", ...)` and emitted via `emit_canonical_error(...)`. The `test_unknown_flag_emits_canonical_error_with_exit_code_2` test (Step 4.7.a) is the load-bearing regression test — assert that `result.exit_code == 2` AND `result.stderr` is exactly one JSON line with `error_code == "cli_argument_error"`.
- **Risk — `_current_run_id` sentinel race.** The global `--run-id` callback writes to a module-level `_current_run_id: RunId = RunId()`. If two concurrent CLI invocations share an interpreter (e.g. test fixtures), the sentinel could be overwritten. Mitigation: this task is a single-process CLI invoked once per process — there is no concurrency. The sentinel is correct for v1. If a future task introduces subprocess parallelism (not on the v1 roadmap per ADR-005), refactor `_current_run_id` to a `ContextVar`.
- **Risk — `RunId` import boundary.** The `interface/errors.py` and `interface/cli_contract.py` modules import from `monte_carlo_risk.domain.shared_kernel` (for `RunId`). This is the only domain import the interface layer may have (per ADR-001/007). Drift risk: a future task that imports from `domain.portfolio`, `domain.simulation`, etc. — a hard violation. Mitigation: Step 4.8's manual import audit enumerates every `interface/` file and asserts the only `monte_carlo_risk.domain` import is `.shared_kernel`. task-004's `.importlinter` will encode `interface → domain.shared_kernel` as a separate contract (or `interface → application`/`infrastructure` as a separate forbidden contract).
- **Risk — `pathlib` in `interface/cli/`.** Per `hexagonal.md` §Linter Contract, `pathlib` is forbidden in `domain/`. The contract does NOT forbid `pathlib` in `interface/cli/`, but the architecture rationale is "pathlib is filesystem I/O; abstract via `OutputWriter` Protocol." For task-003, **no filesystem I/O exists** — the `describe-mock-data` stub returns a hardcoded dict. Drift risk: a future task that adds `--output-dir` to the CLI and writes files via `Path(...)` directly, bypassing the (future) `OutputWriter` port. Mitigation: this task does NOT add filesystem I/O — explicitly documented in the source `task.md` §Out of Scope ("Real mock CSV corpus lands in Epic 003 / task-010"). When `--output-dir` arrives (Epic 002 / task-009 onward), inject an `OutputWriter` port instead of using `pathlib`.
- **Risk — structlog configuration side-effects across tests.** `configure_logging()` mutates global structlog state. If `test_describe_mock_data` runs after `test_logging`, the latter's JSON config may bleed into the formers' output. Mitigation: Step 4.7.c uses an explicit `stream=io.StringIO()` argument, so it does not pollute `sys.stderr`. For the other tests (`test_describe_mock_data`, `test_canonical_error`), use `CliRunner(mix_stderr=False)` so stderr is captured independently. Add a `tests/unit/interface/conftest.py` fixture that calls `configure_logging(log_format="json")` once at module load (idempotent; safe to call multiple times). Alternatively, do not configure logging in the CLI tests at all — Typer's `--log-level` callback runs only when the flag is passed, and `describe-mock-data` does not log, so the default config (structlog unconfigured = pass-through) is fine for these tests. Recommendation: do not configure logging in `test_describe_mock_data.py` / `test_canonical_error.py`; only `test_logging.py` exercises `configure_logging`.
- **Risk — contract version drift.** If the contract bump (Step 4.1) lands in a separate commit from the code, a bisect on `main` will find `cli-contract.yaml` v1.1.0 but the CLI still emitting the old error envelope (or vice versa). Mitigation: Step 4.1 must be the **first commit** in the PR. If the PR is split (Step 6.3), the contract bump ships in PR-A.
- **Risk — `error_code` construction-time validation rejects legitimate new codes.** Step 4.3 says `CanonicalCliError` raises `ValueError` if `error_code` is not in the contract-loaded enum set. If the YAML parse fails (e.g. the contract file is malformed), the entire CLI breaks. Mitigation: load the contract once at module import time; if it fails, log a structlog error and fall back to a minimal in-code enum (just `cli_argument_error` for now) so the CLI still starts. Alternative: don't validate at construction; validate at `emit_canonical_error` time. Trade-off: fail-fast at construction is the ADR-001 / task-002 `Weight` precedent (fail-fast at construction, not deferred). Recommendation: validate at construction with a try/except around the YAML load; on failure, use the in-code fallback list.
- **Risk — `ruff format`/`mypy` strictness on dataclass + frozen + `dict[str, object]`.** `dict[str, object]` requires `from __future__ import annotations` on Python 3.12 (or `dict[str, Any]` on 3.11). The `pyproject.toml` already pins `python_version = "3.12"` for mypy and `target-version = "py312"` for ruff. Mitigation: every new file starts with `from __future__ import annotations` (Steps 4.3–4.7).
- **Failure mode specific to L3 Transport — Typer version drift.** `typer~=0.12` is the pinned range. A future bump to `typer~=0.13` could change `CliRunner.invoke(...)` signature or `BadParameter` semantics. Mitigation: `pyproject.toml` already uses `~=` (compatible-release) which allows patch-level but not minor-level bumps; if a minor bump is required, update Step 4.7's test code and the §4.6.b catch-all together in a single commit.
- **Failure mode specific to L3 Transport — `click` exception type changes.** `typer.BadParameter` is a subclass of `click.exceptions.BadParameter` (which is a subclass of `click.exceptions.UsageError`). Step 4.6.b's catch-all uses `(typer.BadParameter, click.exceptions.UsageError)` to be defensive. If a future Typer version swaps the inheritance, update the tuple.
- **Observability gap — no `--run-id` in log lines (yet).** The `--run-id` global flag is parsed (Step 4.5), the sentinel is set (Step 4.6.b), and the value flows into `CanonicalCliError.run_id` (Step 4.3). But **structlog events do NOT yet include the `run_id` field** — the `contextvars` processor will pick it up once a future task wraps every domain operation in `structlog.contextvars.bind_contextvars(run_id=...)`. Drift risk: a reader of the tracer bullet's stderr cannot correlate a log line with an error line via `run_id`. Mitigation: this is acknowledged in §7 of Epic 006 / task-025 (structlog event wiring), where the explicit binding lands. Not a task-003 problem.
- **Blast radius.** `describe-mock-data` is a stub — its only effect is emitting one JSON line to stdout. If the stub is malformed, the impact is "user runs the command and gets a malformed JSON" — recoverable by re-running. No filesystem writes, no DB, no broker. Rollback: revert the PR. Feature flag: N/A (single-process CLI).
- **Rollback strategy.** `git revert <merge-sha>` on `main`. Because the contract bump (Step 4.1) is a `minor` version (additive, not breaking), reverting the contract file to v1.0.0 is safe — no consumer was depending on `cli_argument_error` before this PR (it is a new code, not a renamed one). The CLI reverts to emitting the previous Typer-style error text on `--bogus`; users get an ugly error but the rest of the CLI works.

## 9. Definition of Done

- [ ] All three BDD scenarios satisfied: **Happy Path** (`describe-mock-data` → exit 0, stdout matches `mock_data_descriptor` stub byte-for-byte), **Sad Path** (`describe-mock-data --bogus` → exit 2, stderr contains exactly one canonical JSON line with `error_code == "cli_argument_error"` and a valid `run_id`), **Edge Case — Mandatory** (`configure_logging(log_format="json", stream=non_tty)` → every emitted event is a single valid JSON line, no multi-line traces, no ANSI colors).
- [ ] All five `Task Breakdown` items ticked (API Changes ✅, DB Migrations N/A — no DB per ADR-009, Feature Flags N/A — single-process CLI per ADR-005, Metrics / Logs ✅, Contract Tests N/A — first contract test lands with task-009).
- [ ] Tests added: `tests/unit/interface/test_canonical_error.py` (4 tests, Sad Path), `tests/unit/interface/test_describe_mock_data.py` (3 tests, Happy Path), `tests/unit/interface/test_logging.py` (3 tests, Edge Case — **added by this plan**, see §7 deviation). No Testcontainers needed (no DB). No Pact needed (no cross-service payload). Unit + CLI integration tests only.
- [ ] CI green: `make lint` (`ruff check` + `ruff format --check` + `mypy src`) and `make test` (`pytest -q --cov=src/monte_carlo_risk --cov-fail-under=0` with ≥ 80 % coverage on `interface/errors.py` and `interface/logging.py`; ≥ 70 % on `interface/cli_contract.py`). PR ≤ 300 LOC (single PR) or ≤ 200 LOC per stacked PR. Squash-merged to `main`; branch deleted.
- [ ] `docker compose run --rm monte-carlo describe-mock-data` exits 0 and prints the stub JSON (verified via `make docker-build && make docker-smoke`).
- [ ] Feature flag (N/A) — no flag registered; recorded as N/A.
- [ ] Logs: structlog configured with JSON renderer by default; non-TTY mode disables ANSI colors; one valid JSON event per line (Edge Case BDD verified by `test_structlog_json_renderer_emits_one_valid_json_per_line_in_non_tty`). No `print(...)` in the new `interface/` modules except the explicit JSON emission paths (`emit_canonical_error` to stderr, `describe_mock_data` to stdout).
- [ ] External HTTP calls: N/A (no network in this task per ADR-005).
- [ ] ORM entity: N/A (no ORM, no DB).
- [ ] Manual import audit (Step 4.8) confirms `src/monte_carlo_risk/interface/` imports **only** `__future__`, `dataclasses`, `io`, `json`, `re`, `sys`, `typing`, `click`, `typer`, `structlog`, `monte_carlo_risk.domain.shared_kernel` (`RunId` only) — pre-empting task-004's `.importlinter` job.
- [ ] `dependency-graph.md` updated: `task-003` → `Done`, unblocking `task-004` (import-linter-and-ci-pipeline).
- [ ] `cli-contract.yaml` bumped to v1.1.0 with `cli_argument_error` enum value; changelog entry added at bottom of file (`# 2026-06-23 v1.1.0 — added error_code "cli_argument_error" (task-003).`).

## 10. Anti-Patterns to Avoid

- **ORM Bleed** — N/A (no ORM, no DB). Drift risk: a future task that adds a `--db-url` flag to the CLI; refuse.
- **CI Bottleneck** — keep this PR's CI to `lint` + `pytest` only; the `domain-purity` / `import-linter` job arrives with task-004 and runs in < 5 s. If the test wall-clock exceeds NFR-2 (5 s full suite), profile and trim — do not defer to task-004.
- **100% Coverage Vanity** — aim for ≥ 80 % line coverage on the new `interface/` modules. The Typer-level integration tests (`CliRunner`) cover the `app()` surface; pure unit tests on `configure_logging` cover the `logging.py` branch table. Do NOT add tests that re-exercise `typer.Typer.__init__` internals — that's testing Typer, not our code.
- **Swallowing Exceptions** — `emit_canonical_error` MUST propagate to `sys.exit(2)` after writing the canonical line. Never wrap in `try/except` to "convert to a friendlier message" — the canonical envelope IS the friendlier message. The domain exceptions from task-002 (`InvalidTickerError`, etc.) MUST propagate up through `app()` until caught at the same boundary that catches `typer.BadParameter` (Step 4.6.b). Once Epic 002 introduces real CLI commands that touch domain code, the catch-all widens to `(typer.BadParameter, click.exceptions.UsageError, ValueError)` and maps each `ValueError` to its corresponding `error_code`.
- **Full-Stack Single Commit** — this PR is pure L3 Transport + one contract edit. Do NOT add the `.importlinter` config (task-004), the `Portfolio` aggregate (task-006), the `simulate` command (task-016), or any other bounded-context code. The source `task.md` §Out of Scope lists exactly what NOT to bundle.
- **Designing in the IDE** — the source `task.md` is precise about the stub shape (`provider`, `version`, `tickers`, `date_range`, `frequency`), the canonical error envelope (`error_code`, `message`, `run_id`), and the new `cli_argument_error` enum value. Do not invent additional stub fields (e.g. `tickers: ["AAPL"]`) that the task does not call for. If the stub feels too minimal, raise it — do not expand scope silently.
- **Long-Lived Branch** — this task is medium-sized (≈ 280 LOC source + 120 LOC tests) but well-scoped; it must merge same-day or next-day. If a reviewer requests sweeping changes, rebase and merge in chunks (Step 6.3 stacked PRs); do not let the branch live > 48h.
- **Stacked PRs Across Layers** — task-004 (linter) MUST wait for this PR; do not bundle `.importlinter` here "to save time." task-016 (`simulate` command extension) MUST wait for task-015 (orchestrator) → task-009 (validate-portfolio CLI) → this PR. The hexagonal boundary is the whole point.
- **Mocking the Database** — N/A (no DB). For the `RunId` round-trip in the Sad Path test, use a real `RunId()` (auto-UUID4) — never mock `uuid.uuid4` itself; the real call is fast and tests the round-trip honestly.
- **Picking Up a Blocked Task** — task-002 is `Done` ✅. Do not start work on task-004 (import-linter), task-005 (portfolio-shared-kernel-extensions), or task-006 (portfolio-aggregate) until this PR merges and `dependency-graph.md` is updated.
- **Typer-as-Application-Layer** — `interface/cli/app.py` is a **composition root**, not a use case. Do not import from `monte_carlo_risk.application.*` here; the orchestrator (`RunSimulation` use case) lands with Epic 003 / task-015. When it does, `app.py` will inject it via Typer callback — not by importing it directly into a command function.
- **`print` outside the two sanctioned emission paths** — `emit_canonical_error` writes to stderr; `describe_mock_data` writes to stdout. No other `print` calls. No `pprint`, no `rich.print`, no `console.log`. If a command needs progress output, it logs via `structlog.get_logger().info(...)` (lands with task-025).
- **`pathlib` in `interface/cli/`** — defer to the future `OutputWriter` port. For this task, no filesystem I/O exists — explicitly verify by reading the diff before opening the PR.
- **Contract version skew** — the `cli-contract.yaml` bump (Step 4.1) MUST be the first commit in the PR. If split into stacked PRs (Step 6.3), the bump ships in PR-A. Never merge code that emits `cli_argument_error` while the contract still says v1.0.0 — that is a silent contract drift.

## Test Results

> **Verdict (initial `400.testing` audit on `main` @ `1bfec7d` on 2026-06-23):** **NO-GO — prerequisites not satisfied.** No test was executed against `main` because the implementation was not built. The skill rule *"do not run tests against missing code"* was binding.

### Artifact-under-test baseline

| Field                                               | Value                                                                                                                                                     |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Commit under test                                   | `1bfec7d` (`Merge pull request #2 from jcarloshg/task-002-shared-kernel-value-objects`)                                                                   |
| Branch with implementation                          | **N/A — no `task-003-cli-describe-mock-data-stub` branch exists**                                                                                         |
| Release artifact SHA                                | **N/A — no release candidate on `main`**                                                                                                                  |
| Container image tag                                 | **N/A — no image built** (the `docker compose run --rm monte-carlo describe-mock-data` invocation that the epic's Story 1.2 requires is not yet possible) |
| Branch under test for the next `400.testing` re-run | `main` after squash-merge of `task-003-cli-describe-mock-data-stub`                                                                                       |
| `dependency-graph.md` status (task-003)             | **Not Done** (row 15 `Status:` still empty)                                                                                                               |
| `cli-contract.yaml` version on disk                 | **v1.0.0** (Step 4.1 not applied)                                                                                                                         |

### Activity 1 — Unit + Integration

| Suite                                                                                                                                   | Result                                               | Report | Notes                                                                                                                |
| --------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------- |
| `pytest tests/unit/interface -q`                                                                                                        | ❌ **NOT RUN**                                        | —      | Test root does not exist on disk (`tests/unit/interface/` missing).                                                  |
| `pytest -q` (full suite)                                                                                                                | ⚠️ **PASS** (inherited from task-002 baseline: 65/65) | local  | 10 task-001 tests + 55 task-002 tests pass. **No task-003 tests added.**                                             |
| `make lint`                                                                                                                             | ⚠️ **PASS** (inherited from task-002 baseline)        | local  | `ruff check src tests` ✅, `ruff format --check src tests` ✅, `mypy src` ✅. **No `interface/` to scan yet.**          |
| `make docker-smoke` (the epic's Story 1.2 invocation)                                                                                   | ❌ **NOT RUN**                                        | —      | `describe-mock-data` is not a registered command — the CLI still prints `__version__` from the task-001 placeholder. |
| BDD Scenario 1 — Happy Path (`describe-mock-data` → exit 0, stdout matches `mock_data_descriptor`)                                      | ❌ **NOT TESTABLE**                                   | —      | The CLI command does not exist; `python -m monte_carlo_risk describe-mock-data` raises `NoSuchCommand`.              |
| BDD Scenario 2 — Sad Path (`describe-mock-data --bogus` → exit 2 + canonical JSON error line with `error_code == "cli_argument_error"`) | ❌ **NOT TESTABLE**                                   | —      | Both the command and the new error_code are absent.                                                                  |
| BDD Scenario 3 — Edge Case — MANDATORY (structlog JSON in non-TTY → one valid JSON per line, no multi-line traces)                      | ❌ **NOT TESTABLE**                                   | —      | `interface/logging.py` is missing; `configure_logging()` is undefined.                                               |

**Domain-purity + interface-purity import audit (Step 4.8 manual preflight, substitute for task-004's `.importlinter`):** ❌ **NOT RUN.** No `interface/` files exist; the audit cannot be performed until §4 lands.

### Activity 2 — Contract Testing

| Suite                                 | Result        | Report | Notes                                                                                                                                                                                          |
| ------------------------------------- | ------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pact consumer-driven contracts        | N/A           | —      | No cross-service payload in this task (this is a CLI, not an HTTP server; per ADR-005 the HTTP `simulate` endpoint is deferred).                                                               |
| AsyncAPI schema-registry validation   | N/A           | —      | No async events emitted by this task. The first AsyncAPI surface is the `risk.report.generated` event (out of scope, arrives with task-019).                                                   |
| `cli-contract.yaml` v1.1.0 validation | ❌ **NOT RUN** | —      | The contract file is **still at v1.0.0** (verified via grep on 2026-06-23); the `cli_argument_error` enum value does not exist. The proposed v1.1.0 bump (§4.1 of this plan) is on paper only. |

### Activity 3 — Non-Functional

| NFR / drill                         | Threshold                                                                             | Measured                                                                                                                                                                                                                                                                              | Result                                                     | Report                                                                     |
| ----------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------- |
| NFR-1 (runtime)                     | < 60 s end-to-end for `--help` and `describe-mock-data`                               | N/A — the CLI command does not exist yet.                                                                                                                                                                                                                                             | ❌ **NOT MEASURED**                                         | —                                                                          |
| NFR-2 (test wall-clock)             | `pytest -q` < 5 s                                                                     | 65/65 pass in < 1 s (inherited from task-002 baseline); the 10 new task-003 tests are not on disk.                                                                                                                                                                                    | ⚠️ **PARTIAL** — baseline passes; new tests not measurable. | local                                                                      |
| NFR-3 (domain purity)               | `.importlinter` passes with zero violations                                           | Not applicable — `.importlinter` arrives with task-004. The 65-test baseline has no boundary violations because there is no `interface/` to violate anything.                                                                                                                         | ⚠️ **VACUOUSLY SATISFIED**                                  | —                                                                          |
| NFR-6 (error contract)              | every CLI failure emits exactly one canonical JSON error line matching `error_schema` | N/A — the CLI has no failure paths yet (the `__main__.py` is still `print(__version__)`).                                                                                                                                                                                             | ❌ **NOT MEASURED**                                         | —                                                                          |
| NFR-7 (Python ≥ 3.12)               | runtime                                                                               | The repo's `.python-version` (4 bytes) pins Python ≥ 3.12 (verified at task-001, unchanged).                                                                                                                                                                                          | ✅ **PASS** (inherited from task-001/002)                   | `cat .python-version`                                                      |
| SAST (ruff `S`/`B`)                 | 0 critical                                                                            | The existing 8 `src/` + 9 `tests/` files pass ruff; no new files to scan.                                                                                                                                                                                                             | ⚠️ **PARTIAL** — baseline passes; new files not scannable.  | local                                                                      |
| DAST                                | n/a                                                                                   | —                                                                                                                                                                                                                                                                                     | N/A                                                        | CLI-only per ADR-005; no HTTP surface.                                     |
| SCA (`pip-audit` on `[dev]` extras) | 0 critical CVEs                                                                       | Not run for this audit — the proposed `interface/` files introduce no new third-party dependencies (`typer~=0.12` + `structlog~=24.4` are already declared in `pyproject.toml` and inherited from task-001). When §4 lands, run `pip-audit -r <(pip freeze)` against the new install. | ⚠️ **DEFERRED**                                             | —                                                                          |
| Chaos drill (FIS / Chaos Mesh)      | n/a                                                                                   | —                                                                                                                                                                                                                                                                                     | N/A                                                        | No network, no DB, no broker. The first chaos drill arrives with task-027. |

### Activity 4 — Shift-Right

| Control                              | Status | Notes                                                                                                                                                                                                      |
| ------------------------------------ | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Feature flag                         | N/A    | Single-process CLI per ADR-005; the source `task.md` §Task Breakdown records `Feature Flags: N/A`.                                                                                                         |
| Canary / blue-green                  | N/A    | No deployable surface in this task. The first canary wiring lands with task-024 (Visualization extension).                                                                                                 |
| Synthetic monitor (top 3–5 journeys) | N/A    | The first user-facing journey to monitor — `docker compose run --rm monte-carlo describe-mock-data` — does not exist yet. The synthetic monitor for it lands with task-028 (e2e-docker-smoke-golden-file). |
| Auto-rollback on SLO breach          | N/A    | No SLO surface yet. First auto-rollback wired with task-024.                                                                                                                                               |
| PagerDuty wiring                     | N/A    | First page-worthy alarm lands with task-024 (visualization failure) and task-027 (NFR-1 breach).                                                                                                           |

### Per-BDD pass/fail matrix (consolidated)

| Source `task.md` §Acceptance Criteria | Plan §5 row             | Test invoked                                                                                    | Verdict            | Evidence                                                                 |
| ------------------------------------- | ----------------------- | ----------------------------------------------------------------------------------------------- | ------------------ | ------------------------------------------------------------------------ |
| **Scenario 1 (Happy Path)**           | `Happy Path`            | `test_describe_mock_data_returns_stub_matching_contract` (proposed in §5/§7.7.b)                | ❌ **NOT TESTABLE** | Test file `tests/unit/interface/test_describe_mock_data.py` not on disk. |
| **Scenario 2 (Sad Path)**             | `Sad Path`              | `test_unknown_flag_emits_canonical_error_with_exit_code_2` (proposed in §5/§7.7.a)              | ❌ **NOT TESTABLE** | Test file `tests/unit/interface/test_canonical_error.py` not on disk.    |
| **Edge Case (Mandatory)**             | `Edge Case — MANDATORY` | `test_structlog_json_renderer_emits_one_valid_json_per_line_in_non_tty` (proposed in §5/§7.7.c) | ❌ **NOT TESTABLE** | Test file `tests/unit/interface/test_logging.py` not on disk.            |

### Anti-pattern self-check

- ✅ **No Plan Path** — single `plan.md` provided (just produced by `300.plan-coding`), mutation in place.
- ✅ **No new `04.testing.md`** — all results live inside this `plan.md`.
- ✅ **No Tick-and-Forget** — zero BDD boxes ticked; zero fake test-report URLs invented.
- ✅ **No Testing `main`** — explicitly identified that `main` @ `1bfec7d` only contains task-001 + task-002; this plan refuses to certify task-003 against the task-002 commit.
- ✅ **No Mocking the ORM** — vacuously satisfied (no ORM in scope).
- ✅ **No Ice Cream Cone** — vacuously satisfied.
- ✅ **No Shared Staging as Safety Net** — vacuously satisfied.
- ✅ **No "We'll Load Test Right Before Launch"** — no k6 nightly yet; this task has no HTTP surface to load-test.
- ✅ **No Manual QA Sign-Off** — sign-off is auto-recorded as **NOT ISSUED** until a real merge produces a SHA-pinned artifact.
- ✅ **No silent draft** — the `## Certified Release Candidate` stamp below is explicit, not missing.

## Certified Release Candidate

> **Status: ❌ NOT ISSUED — implementation not built; no SHA-pinned release artifact on `main`.**
>
> A `plan.md` without a `Certified Release Candidate` stamp is a draft, not a release candidate (anti-pattern *"Passing the Plan Without Certification Stamp"*). This plan therefore carries an explicit **NOT ISSUED** stamp so the negative result is machine-checkable, not silent. All 16 §7 artifacts are missing (see `### Blocker — Implementation Not Built` in §2 and `## Test Results`); certification awaits the merge.

| Field                                               | Value                                                                                                                                                                                                                                                                                                                                                                                            |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Release candidate tag                               | **NOT ISSUED**                                                                                                                                                                                                                                                                                                                                                                                   |
| SHA-pinned image tag                                | **N/A**                                                                                                                                                                                                                                                                                                                                                                                          |
| `release/release-candidate.tag` (signed)            | **N/A — file does not exist; would be created at `release/release-candidate.tag` once a release exists**                                                                                                                                                                                                                                                                                         |
| SLO compliance row                                  | **N/A — no SLO surface in this task**                                                                                                                                                                                                                                                                                                                                                            |
| Sign-off timestamp                                  | **N/A — no sign-off, because no candidate**                                                                                                                                                                                                                                                                                                                                                      |
| Canary config (`release/canary-config.yaml`)        | **N/A — not produced**                                                                                                                                                                                                                                                                                                                                                                           |
| Feature-flag registry (`release/feature-flags.yml`) | **N/A — N/A per ADR-005; recorded as such in `task.md` §Task Breakdown**                                                                                                                                                                                                                                                                                                                         |
| Auto-rollback wiring                                | **N/A — no deployable surface in this task**                                                                                                                                                                                                                                                                                                                                                     |
| Owner of the next attempt                           | The implementer of task-003 (per §6 "PR + Merge"). Once the PR is opened and squash-merged to `main`, re-invoke `400.testing` against the same path. The skill will re-verify §7 artifacts against the merge commit, run the four activities, tick the BDD boxes with linked test reports, and replace this `NOT ISSUED` stamp with a positive `ISSUED` stamp carrying the release artifact SHA. |

**Re-entry protocol:** once the task-003 PR is merged and `dependency-graph.md` row 15 reads `Status: Done` on `main`, re-invoke the `400.testing` skill with the same path. The skill will re-verify §7 artifacts, run the four activities, tick the BDD boxes with linked test reports, and replace this `NOT ISSUED` stamp with a positive `ISSUED` stamp carrying the release artifact SHA.

## Quick-Reference Summary

### Mission
Land the first user-facing CLI surface — a working `monte-carlo describe-mock-data` command — together with the canonical JSON error envelope and the structlog setup that every later Epic depends on. This is the Tracer Bullet's one end-to-end vertical slice: Typer root → JSON stdout → JSON stderr envelope → JSON logs → Docker invocation. Traces to Story 1.2.

### Key Decisions (carried from `300.plan-coding`, unchanged by `400.testing`)
- **L3 Transport only.** No L1 data layer (ADR-009). No L2 domain code (re-uses `RunId` from task-002). No L4 defense (linter arrives with task-004 — Step 4.8 manual audit substitutes). No L5 delivery (single-process CLI per ADR-005).
- **Composition root in `interface/cli/app.py` only.** Per ADR-001 / hexagonal §Concrete Layout, `app.py` is the **only** file in `interface/` that knows about Typer — every command function (`describe_mock_data`) stays a plain Python function, unit-testable without `CliRunner`.
- **Canonical error envelope = exactly one JSON line to stderr.** `emit_canonical_error` writes a single line matching `cli-contract.yaml` §`error_schema`, then exits with the documented code. No multi-line JSON, no prefix text, no ANSI.
- **Unknown-flag catch-all in `__main__.py`.** `app()` is wrapped in `try/except (typer.BadParameter, click.exceptions.UsageError)` so Typer's built-in error text is converted to the canonical envelope before reaching the user.
- **structlog `dict_tracebacks` + `JSONRenderer(sort_keys=True)`.** Ensures exception traces collapse to single-line structured fields. The `colors=False` default in non-TTY mode is the load-bearing line for the Edge Case BDD.
- **Contract minor bump (v1.0.0 → v1.1.0) ships in the same PR.** Per `cli-contract.yaml` §Versioning Rules, adding an enum value is a `minor` bump. The bump is the **first commit** in the PR to avoid contract/code skew during bisect.
- **`RunId` is the **only** domain import in `interface/`.** Enforced by Step 4.8's manual import audit. task-004's `.importlinter` will automate this.

### Key Decisions (appended by `400.testing` on 2026-06-23)
- **Certify only what is built.** No code → no `pytest` invocation → no BDD ticks → no `Certified Release Candidate`. The plan is returned to the implementer with an explicit blocker table.
- **Do not fabricate evidence.** Per the testing-phase anti-pattern *"Tick-and-Forget"* and the rule *"do not run tests against missing code"*, all BDD boxes stay `[ ]`, all §7 rows stay `[ ]`, and no synthetic test-report URL is invented.
- **Use the existing pre-flight gate.** The dependency-graph row (row 15) for task-003 still has `Status:` blank — it is the source-of-truth gate that should have blocked entry to `400.testing`. The skill has now propagated that fact into the plan itself.

### Critical Artifacts
- Code: `src/monte_carlo_risk/interface/{__init__.py, errors.py, logging.py, cli_contract.py}`, `src/monte_carlo_risk/interface/cli/{__init__.py, app.py}`, `src/monte_carlo_risk/interface/cli/commands/{__init__.py, describe_mock_data.py}`, modified `src/monte_carlo_risk/__main__.py`. **❌ None built** — see blocker table in §2.
- Tests: `tests/unit/interface/{__init__.py, test_canonical_error.py, test_describe_mock_data.py, test_logging.py}`, `tests/unit/interface/cli/{__init__.py, commands/__init__.py}`. **❌ None built.**
- Contract: modified `docs/monte-carlo-risk/100.planning/contracts/cli-contract.yaml`. **❌ Not modified** — still v1.0.0; `cli_argument_error` not added.
- No migration, no new contract file, no feature-flag entry.
- Repo setup touched: none proposed (`pyproject.toml` already declares `typer~=0.12` and `structlog~=24.4`).
- Release artifact SHA: **N/A — no release candidate produced.**
- Test reports: **N/A — no test run executed.**

### Open Blockers (refreshed by `400.testing` on 2026-06-23)
- ❌ **task-003 implementation not built.** All 16 §7 artifacts missing on disk (no `interface/` directory, no `tests/unit/interface/` directory, `cli-contract.yaml` not bumped, `__main__.py` not modified). `dependency-graph.md` row 15 `Status:` still empty. **Owner: implementer of task-003.** **Needed by: PR merge to `main`.** Once the PR is opened and squash-merged, re-invoke `400.testing` against this same `plan.md` path.
- ✅ task-002 (`shared-kernel-value-objects`) — `Done`.
- ✅ task-001 (`dev-tooling-bootstrap`) — `Done`.

### Next-Phase Handoff (refreshed by `400.testing` on 2026-06-23)
- **To the implementer (PR + merge step):** open the PR titled `task-003: CLI describe-mock-data Stub + Error Envelope + structlog` from branch `task-003-cli-describe-mock-data-stub` against `main`. PR description should call out: BDD Happy/Sad/Edge satisfaction (cite the 10 new tests after they land), Out-of-Scope adherence (no `simulate`/`validate-portfolio`, no real CSV corpus, no event emission), the §7 deviation (`test_logging.py` added beyond source deliverables), and the LOC budget (single PR ≈ 400 LOC; recommend stacked split per §6.3). Squash-merge to `main`; mark task-003 `Done` in `dependency-graph.md` row 15; then re-invoke `400.testing` against this same `plan.md` path.
- **To the next `400.testing` re-run:** the inputs to consume are: this same `plan.md` (now with §7 artifact paths flipped from ❌ to ✅ once the PR lands), the source `task.md`, the 9 source files under `src/monte_carlo_risk/interface/`, the 6 test files under `tests/unit/interface/`, the modified `cli-contract.yaml` v1.1.0, and the modified `__main__.py`. The four activities to execute: **Unit + Integration** (`pytest -q` against the new test root; NFR-2 wall-clock < 5 s for the new CLI tests), **Contract Testing** (verify `cli-contract.yaml` v1.1.0 YAML parses cleanly; assert `error_schema.error_code.enum` contains the new `cli_argument_error` value), **Non-Functional** (`make lint` passes; `make docker-build && docker compose run --rm monte-carlo describe-mock-data` exits 0 with the stub JSON; `docker compose run --rm monte-carlo describe-mock-data --bogus` exits 2 with the canonical JSON error line on stderr; NFR-2 wall-clock < 5 s; NFR-7 Python ≥ 3.12), **Shift-Right** (N/A — single-process CLI per ADR-005; no canary, no flag, no PagerDuty).
- **To deployment:** nothing is handoff-ready yet. There is no `release/release-candidate.tag`, no `release/canary-config.yaml`, no `release/feature-flags.yml`. The `## Certified Release Candidate` section above is stamped **NOT ISSUED** and will be replaced with `ISSUED` once the PR merges to `main` and `400.testing` produces a SHA-pinned image tag.
