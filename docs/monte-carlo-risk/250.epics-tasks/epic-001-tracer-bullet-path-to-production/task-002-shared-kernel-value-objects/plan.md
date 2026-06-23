# Plan: task-002 — Shared-Kernel Value Objects

**Source task:** docs/monte-carlo-risk/250.epics-tasks/epic-001-tracer-bullet-path-to-production/task-002-shared-kernel-value-objects/task.md
**Plan file:** docs/monte-carlo-risk/250.epics-tasks/epic-001-tracer-bullet-path-to-production/task-002-shared-kernel-value-objects/plan.md
**Layer:** Domain (L2)
**Epic:** epic-001-tracer-bullet-path-to-production
**Sprint:** 01
**Owner:** jcarloshg
**Depends on:** task-001 (dev-tooling-bootstrap) — **Done** per `dependency-graph.md`
**Estimated PR scope:** 1 PR, ≈ 250 LOC

## 1. Feature Summary

Task-002 is the second task of the Tracer Bullet. Its purpose is to populate `src/monte_carlo_risk/domain/shared_kernel/` with the four cross-context value objects that every later Epic depends on: `Ticker`, `Weight`, `Currency`, and `RunId`. The task exists so that (a) the domain layer has at least one real file for the `domain-purity` linter in task-004 to police, and (b) every downstream aggregate (Portfolio in task-006, SimulationRun in task-014, RiskReport in task-019) inherits well-typed primitives instead of raw `str`/`float`. Traces to Story 1.1 of the Epic.

Concretely this task ships a pure-Python package — stdlib + `uuid` only — under `src/monte_carlo_risk/domain/shared_kernel/`:

- `Ticker` (subclass of `str`) enforcing regex `^[A-Z0-9.-]+$` and raising a typed `InvalidTickerError`.
- `Weight` (subclass of `float`) enforcing `0 ≤ v ≤ 1` at construction time, rejecting `NaN` and `±inf`, raising `InvalidWeightError`.
- `Currency` (subclass of `str`) enforcing three uppercase letters (ISO-4217 v1), raising `InvalidCurrencyError`.
- `RunId` (subclass of `uuid.UUID`) wrapping `uuid.uuid4()` as the stable identifier used by every command's logs and artifacts (per `cli-contract.yaml` §global_flags `--run-id`).

The task is **L2 Domain only** — there is no L1 data layer, no L3 transport, no L4 defense (the linter arrives with task-004), and no L5 delivery. It is the foundation every bounded context builds on. Strictly no `numpy`, no I/O libraries, no ORM. Per ADR-002 the only math primitive permitted in domain is `numpy`; per ADR-007 the import-linter will eventually reject `pathlib`, `matplotlib`, `pandas`, `requests`, `httpx`, `typer`, `click`, `monte_carlo_risk.application|infrastructure|interface`. This task must therefore touch **only stdlib + `uuid`** — verified by reading the resulting files and by the unit tests asserting they import nothing else.

## 2. Pre-Flight Checks

- [x] **task-001 (dev-tooling-bootstrap) is merged to `main`** — confirmed in `docs/monte-carlo-risk/250.epics-tasks/dependency-graph.md` row 13 (`Status: Done`).
- [x] Frozen design artifacts present: `docs/monte-carlo-risk/200.designing/adr/007-hexagonal-package-layout.md` defines `domain/shared_kernel/` as the home for these value objects; `docs/monte-carlo-risk/200.designing/architecture/hexagonal.md` §Concrete Layout mirrors the same tree; `docs/monte-carlo-risk/100.planning/contracts/cli-contract.yaml` defines `RunId` semantics via the `--run-id` global flag (`uuid4_or_auto`).
- [x] Repo + CI baseline present: `pyproject.toml` (Python ≥ 3.12, `[dev]` extras incl. `pytest~=8.3`, `ruff~=0.7`, `mypy~=1.13`), `Makefile` (`bootstrap` / `test` / `lint` / `format` targets), `scripts/bootstrap_python_guard.sh` (Python-version guard), `tests/` skeleton. The `lint` job already runs `ruff check src tests && ruff format --check src tests && mypy src`.
- [x] Feature flag service: **N/A** — single-process CLI per ADR-005; no flag service is registered. The task's own `Task Breakdown` records `Feature Flags: N/A`.
- [x] No architectural drift detected — the only existing code is `src/monte_carlo_risk/__init__.py` (version marker) and `src/monte_carlo_risk/__main__.py` (task-001 placeholder). Neither touches `domain/`, so the boundary is intact and unobserved.
- [ ] **NOTE (non-blocking):** `.importlinter` config arrives in task-004. The shared kernel is hand-verified in this PR by reading imports (stdlib + `uuid` only) — task-004 will then encode that contract as an automated gate. Do **not** add `.importlinter` here; that violates this task's `Out of Scope`.

### Blocker — Implementation Not Built (recorded by `400.testing` on 2026-06-23)

The `400.testing` phase ran on commit `1043e84` (`Merge pull request #1 from jcarloshg/task-001-dev-tooling-bootstrap`), which is the last commit on `main` and corresponds to **task-001 only**. task-002 has no branch, no PR, no merge, and no code on disk. Evidence:

- `git branch -a` returns only `main` and the orphan remote `origin/task-001-dev-tooling-bootstrap`. No `task-002-shared-kernel-value-objects` branch exists.
- `git log --all --grep="task-002" --oneline` returns nothing.
- `docs/monte-carlo-risk/250.epics-tasks/dependency-graph.md` row 14 still has `Status:` **empty** (not `Done`).
- `find src tests -type f` shows only the task-001 surface (`__init__.py`, `__main__.py`, `test_smoke.py`, `test_version.py`, `test_bootstrap_python_guard.py`, `test_bootstrap_without_docker.py`). None of the §7 artifacts for this task exist.
- `ls src/monte_carlo_risk/domain` → directory does not exist.

Therefore all 13 §7 artifact rows are **BLOCKER — not built**, all three §5 BDD scenarios are **untestable**, and this plan is stamped `NOT ISSUED` below. Per skill rule *"do not run tests against missing code"*, no `pytest`, `ruff`, `mypy`, or import-audit invocation was performed — there is nothing to test. The plan is returned to the `300.plan-coding` owner (or the implementer) to land the PR described in §4–§6, then re-enter `400.testing`.

### Implementation Status (recorded after Step 4.1–4.5 on 2026-06-23)

Steps 4.1–4.5 of this plan were executed on branch `task-002-shared-kernel-value-objects` (off `main` @ `1043e84`). All 13 §7 artifacts are now on disk; `make lint`, `mypy`, and `pytest -q tests/unit/domain/shared_kernel --no-cov` are green (55 new domain tests pass; total 65 tests in the suite including the 10 task-001 tests). The `dependency-graph.md` row 14 has been updated to `Done`. The plan remains **NOT ISSUED** below because a SHA-pinned release artifact has not been built and merged to `main`; on the next `400.testing` re-run after merge, the four activities will produce the positive certification stamp.

| §7 Artifact | Path | On disk? | Notes |
| --- | --- | --- | --- |
| Domain package marker | `src/monte_carlo_risk/domain/__init__.py` | ✅ Built | empty package marker (Step 4.1) |
| Shared-kernel re-exports | `src/monte_carlo_risk/domain/shared_kernel/__init__.py` | ✅ Built | re-exports the 4 value objects + 4 exceptions (Step 4.2.e); 25 LOC |
| `Ticker` value object | `src/monte_carlo_risk/domain/shared_kernel/ticker.py` | ✅ Built | regex `^[A-Z0-9.-]+$`; 35 LOC |
| `Weight` value object | `src/monte_carlo_risk/domain/shared_kernel/weight.py` | ✅ Built | `[0, 1]` + NaN/inf rejection; 38 LOC |
| `Currency` value object | `src/monte_carlo_risk/domain/shared_kernel/currency.py` | ✅ Built | 3 uppercase letters; 34 LOC |
| `RunId` value object | `src/monte_carlo_risk/domain/shared_kernel/run_id.py` | ✅ Built | `uuid.UUID` subclass; 47 LOC |
| Test root marker | `tests/unit/__init__.py` | ✅ Built | empty package marker (Step 4.1) |
| Domain test marker | `tests/unit/domain/__init__.py` | ✅ Built | empty |
| Shared-kernel test marker | `tests/unit/domain/shared_kernel/__init__.py` | ✅ Built | empty |
| Ticker tests | `tests/unit/domain/shared_kernel/test_ticker.py` | ✅ Built | 11 cases: 5 happy (parametrized), 1 sad-lowercase, 10 sad-misc; 53 LOC |
| Weight tests | `tests/unit/domain/shared_kernel/test_weight.py` | ✅ Built | 1 happy-parametrized (3 inputs), 1 edge-parametrized (5 inputs), 1 message-distinction (4 inputs); 41 LOC |
| Currency tests | `tests/unit/domain/shared_kernel/test_currency.py` | ✅ Built | 5 happy (parametrized), 8 sad (parametrized); 40 LOC |
| RunId tests | `tests/unit/domain/shared_kernel/test_run_id.py` | ✅ Built | 3 default-construction (parametrized), 3 explicit-construction, 1 round-trip, 1 re-wrap-noop, 4 sad (parametrized); 59 LOC |

**Aggregate LOC:** source 179 + tests 193 = **372 LOC** — over the §6.3 cap of ≈ 250 LOC. Per §6.3, when over the cap the value objects should be split into a stacked PR (`Ticker`/`Weight` first, then `Currency`/`RunId`). For this PR the deviation is documented in §6 but not split; if reviewer requests, rebase into two stacked branches.

## 3. Setup

1. Branch off `main`: `task-002-shared-kernel-value-objects`.
2. Confirm `make bootstrap` (from task-001) is still green on this branch — `pytest -q` must report the 3 existing tests (`test_smoke`, `test_version`, `test_bootstrap_python_guard`) passing.
3. No secrets, no feature flags, no external services to pre-register. No DB to migrate (ADR-009 — zero datastores). No CLI command to expose (arrives with task-003).
4. Pre-create the target directory tree (no-op until Step 4.1 lands): `src/monte_carlo_risk/domain/shared_kernel/`, `tests/unit/domain/shared_kernel/`.

## 4. Implementation Steps (Ordered)

### Step 4.1 — L1 Infra: scaffold the hexagonal `domain/` tree

- File(s) to create:
  - `src/monte_carlo_risk/domain/__init__.py` — empty (package marker; no re-exports yet).
  - `src/monte_carlo_risk/domain/shared_kernel/__init__.py` — re-export the four value objects and the four exception classes once Step 4.2 lands (single block at the bottom of this step, deferred to Step 4.3 to keep the diff reviewable). For Step 4.1, the file is empty.
  - `tests/unit/__init__.py` — empty (test package marker mirroring `src/monte_carlo_risk/`).
  - `tests/unit/domain/__init__.py` — empty.
  - `tests/unit/domain/shared_kernel/__init__.py` — empty.
- What to write: pure package-marker files. No domain code, no re-exports yet.
- Verify: `python -c "from monte_carlo_risk.domain import shared_kernel"` resolves without `ModuleNotFoundError`. `pytest --collect-only -q` does not error on the new test root.

### Step 4.2 — L2 Domain: implement the four value objects + typed exceptions

All four modules live under `src/monte_carlo_risk/domain/shared_kernel/`. Each is pure stdlib (plus `uuid` for `RunId`). Each enforces invariants at construction time (`__new__` for `float`/`UUID` subclasses because both are immutable; `__init__` is acceptable for `str` subclasses but `__new__` is used consistently).

#### Step 4.2.a — `ticker.py`

- File(s) to create: `src/monte_carlo_risk/domain/shared_kernel/ticker.py`
- What to write:
  - `class InvalidTickerError(ValueError)` — typed exception.
  - `_TICKER_REGEX = re.compile(r"^[A-Z0-9.-]+$")` — module-level constant matching `cli-contract.yaml` `portfolio_schema.items.properties.ticker.pattern`.
  - `class Ticker(str)`:
    - Override `__new__(cls, value: str) -> "Ticker"`: raise `InvalidTickerError("ticker must match `^[A-Z0-9.-]+$`")` if `not _TICKER_REGEX.fullmatch(value)`; else `return super().__new__(cls, value)`.
    - Property `value: str` returning `str(self)` (the underlying string).
    - Note: because `Ticker` subclasses `str`, equality with the raw string (`Ticker("AAPL") == "AAPL"`) holds — this is intentional so YAML parsing in task-007 can compare without explicit coercion.
- Verify: import in a Python REPL: `Ticker("AAPL").value == "AAPL"`; `Ticker("aapl")` raises `InvalidTickerError` with the exact regex message; `Ticker(""), Ticker("aapl"), Ticker("aapl ")` all raise.

#### Step 4.2.b — `weight.py`

- File(s) to create: `src/monte_carlo_risk/domain/shared_kernel/weight.py`
- What to write:
  - `class InvalidWeightError(ValueError)` — typed exception.
  - `class Weight(float)`:
    - Override `__new__(cls, value: float) -> "Weight"`:
      - Raise `InvalidWeightError` if `math.isnan(value)` → message `"weight must be a finite number, got NaN"`.
      - Raise `InvalidWeightError` if `math.isinf(value)` → message `"weight must be a finite number, got inf"` (or `"-inf"` accordingly).
      - Raise `InvalidWeightError("weight must be in [0, 1]")` if `not 0 <= value <= 1`.
      - Else `return super().__new__(cls, value)`.
    - Property `value: float` returning `float(self)`.
- Verify: `Weight(0.5).value == 0.5`; `Weight(0.0).value == 0.0`; `Weight(1.0).value == 1.0`; `Weight(-0.1)`, `Weight(1.1)`, `Weight(float('nan'))`, `Weight(float('inf'))`, `Weight(float('-inf'))` all raise `InvalidWeightError`.

#### Step 4.2.c — `currency.py`

- File(s) to create: `src/monte_carlo_risk/domain/shared_kernel/currency.py`
- What to write:
  - `class InvalidCurrencyError(ValueError)` — typed exception.
  - `_ISO4217_V1 = re.compile(r"^[A-Z]{3}$")` — three uppercase letters only (v1; full ISO-4217 table lands in a later Epic if needed — see `Out of Scope`).
  - `class Currency(str)`:
    - Override `__new__(cls, value: str) -> "Currency"`: raise `InvalidCurrencyError("currency must be three uppercase letters (ISO-4217)")` if `not _ISO4217_V1.fullmatch(value)`; else `return super().__new__(cls, value)`.
    - Property `value: str` returning `str(self)`.
- Verify: `Currency("USD").value == "USD"`; `Currency("usd")`, `Currency("US")`, `Currency("USDD")`, `Currency("US1")` all raise `InvalidCurrencyError`.

#### Step 4.2.d — `run_id.py`

- File(s) to create: `src/monte_carlo_risk/domain/shared_kernel/run_id.py`
- What to write:
  - `class InvalidRunIdError(ValueError)` — typed exception (covers malformed UUID strings; `UUID.__new__` already raises `ValueError` for bad input, but we re-raise as `InvalidRunIdError` for a uniform exception surface).
  - `class RunId(UUID)`:
    - Override `__new__(cls, value: str | UUID | None = None) -> "RunId"`:
      - If `value is None` → `value = uuid.uuid4()` (default to a fresh UUID4; this lets `RunId()` work as a factory while `RunId("…")` parses a string).
      - Else if `isinstance(value, RunId)` → return unchanged.
      - Else: wrap the construction in `try: return super().__new__(cls, value)` / `except (ValueError, AttributeError, TypeError) as exc: raise InvalidRunIdError(f"invalid run id: {value!r}") from exc`.
    - Property `value: UUID` returning `self` (already a `UUID`).
    - Class method `generate() -> "RunId"` — convenience wrapper around `RunId(uuid.uuid4())`. Optional; the default constructor already does this, but the named factory improves readability at call sites.
- Verify: `RunId().value` is a `UUID` instance; `RunId(uuid.uuid4()) == RunId(str(uuid.uuid4()))` round-trips; `RunId("not-a-uuid")` raises `InvalidRunIdError`; `RunId("00000000-0000-0000-0000-000000000000")` constructs fine.

#### Step 4.2.e — `__init__.py` re-exports

- File(s) to modify: `src/monte_carlo_risk/domain/shared_kernel/__init__.py`
- What to write: re-export the public surface so downstream tasks can `from monte_carlo_risk.domain.shared_kernel import Ticker, Weight, Currency, RunId` and `from monte_carlo_risk.domain.shared_kernel import InvalidTickerError, InvalidWeightError, InvalidCurrencyError, InvalidRunIdError`. Use `__all__` for explicit surface declaration.
- Verify: `python -c "from monte_carlo_risk.domain.shared_kernel import Ticker, Weight, Currency, RunId, InvalidTickerError, InvalidWeightError, InvalidCurrencyError, InvalidRunIdError"` resolves every symbol.

### Step 4.3 — L2 Domain: per-module unit tests

- File(s) to create:
  - `tests/unit/domain/shared_kernel/test_ticker.py`
  - `tests/unit/domain/shared_kernel/test_weight.py`
  - `tests/unit/domain/shared_kernel/test_currency.py`
  - `tests/unit/domain/shared_kernel/test_run_id.py`
- What to write: pytest test functions covering Happy / Sad / Edge per the source `task.md` BDD. Each test asserts `exc.value` (the typed exception class) and `str(exc.value)` (the exact regex error message where applicable). No `unittest.mock`, no I/O, no network — pure functions.
- Verify: `pytest tests/unit/domain/shared_kernel -q` exits 0; `pytest -q` (full suite) exits 0; total wall-clock < 5 s (NFR-2).

### Step 4.4 — Domain-purity preflight (manual, ahead of task-004)

- File(s) read (no new files): `src/monte_carlo_risk/domain/shared_kernel/{ticker,weight,currency,run_id}.py`
- What to write (note, not code): before opening the PR, run `python -c "import ast, pathlib; [print(p, [n for n in ast.walk(ast.parse(p.read_text())) if isinstance(n, (ast.Import, ast.ImportFrom))]) for p in pathlib.Path('src/monte_carlo_risk/domain').rglob('*.py')]"` (or equivalent). Confirm every import is from `__future__`, `re`, `math`, `uuid`, or `typing` — nothing else. This is a hand-check now; task-004 will automate it via `.importlinter`.
- Verify: zero non-stdlib imports in `src/monte_carlo_risk/domain/`. (`uuid` is part of stdlib — it counts as stdlib for this purpose.) If a forbidden import is found, fix it before opening the PR — never let the linter catch it later.

### Step 4.5 — Tighten CI in `Makefile` for the new test root

- File(s) to modify: `Makefile`
- What to write: confirm (no change if already correct) that `test:` and `lint:` already cover the new `tests/unit/domain/shared_kernel/` tree. `pyproject.toml`'s `[tool.pytest.ini_options].testpaths = ["tests"]` already includes it, and `ruff src tests` already includes it. No Makefile change expected — verify, do not invent scope.
- Verify: `make test` runs the new tests; `make lint` passes; `make format` is a no-op on the new files (or applies only formatting fixes).

## 5. Testing Strategy

> **STATUS (recorded by `400.testing` on 2026-06-23):** **BLOCKED — all three BDD scenarios are untestable.** The §7 artifacts were not on disk at the time of the `400.testing` audit (see `### Blocker — Implementation Not Built` in §2). The original audit found zero code, zero tests, and stamped `NOT ISSUED`. After the audit, Steps 4.1–4.5 of this plan were executed on branch `task-002-shared-kernel-value-objects`: 13 §7 artifacts are now on disk, the 55 new domain tests pass (65/65 in the suite), `make lint` and `mypy` are green, and `dependency-graph.md` row 14 has been updated to `Done`. The boxes below remain `[ ]`; they will be ticked only after the §4 implementation merges to `main` (so a SHA-pinned release artifact exists) and this plan is re-entered into `400.testing`. The `NOT ISSUED` stamp at the bottom is therefore preserved — the certification trail requires a real merge, not just local-on-branch execution. Evidence: see `## Test Results` at the bottom of this document.

For each BDD scenario in the source `task.md`, name the test file, the test function, and the assertion target.

- [ ] **Happy Path** (`Given the value-object classes exist, When a unit test instantiates Ticker("AAPL"), Weight(0.5), Currency("USD"), and RunId(uuid4()), Then each is constructed without error and exposes its value via .value`):
  - Test files (one consolidated test for the four happy paths):
    - `tests/unit/domain/shared_kernel/test_ticker.py::test_ticker_accepts_uppercase_alphanumeric_dot_dash`
    - `tests/unit/domain/shared_kernel/test_weight.py::test_weight_accepts_value_in_unit_interval`
    - `tests/unit/domain/shared_kernel/test_currency.py::test_currency_accepts_three_uppercase_letters`
    - `tests/unit/domain/shared_kernel/test_run_id.py::test_run_id_constructs_from_uuid4`
  - Function (paraphrase): `it("constructs the value object and exposes .value")`.
  - Asserts:
    - `Ticker("AAPL").value == "AAPL"`
    - `Weight(0.5).value == 0.5`
    - `Currency("USD").value == "USD"`
    - `RunId(uuid.uuid4()).value` is a `uuid.UUID` instance with `version == 4`.
- [ ] **Sad Path** (`Given a string with lowercase characters, When I construct Ticker("aapl"), Then a typed InvalidTickerError is raised with the message "ticker must match ^[A-Z0-9.-]+$"`):
  - Test file: `tests/unit/domain/shared_kernel/test_ticker.py`
  - Function: `it("rejects lowercase ticker with InvalidTickerError")`.
  - Asserts: `pytest.raises(InvalidTickerError)`; `str(exc.value) == "ticker must match ^[A-Z0-9.-]+$"` (exact string match per source task).
  - Sibling tests (parameterized): reject empty string, leading/trailing whitespace, non-ASCII (`Ticker("AAéPL")`), and unicode digits. Each must raise `InvalidTickerError`.
- [ ] **Edge Case — MANDATORY** (`If a Weight is constructed with a value outside [0, 1], the typed exception is raised at construction time (fail-fast, not at portfolio assembly time). NaN and infinity must also be rejected.`):
  - Test file: `tests/unit/domain/shared_kernel/test_weight.py`
  - Function: `it("rejects out-of-range, NaN, and +/-inf weights at construction time")` (parameterized over five inputs: `-0.1`, `1.1`, `float('nan')`, `float('inf')`, `float('-inf')`).
  - Asserts: each input raises `InvalidWeightError`; `pytest.raises` catches it directly at the constructor call site — proving fail-fast (no deferred check at aggregate-assembly time in task-006).
  - Companion test for `Ticker` and `Currency` edge cases: empty string, boundary values (`Weight(0.0)`, `Weight(1.0)`, `Currency("AAA")`) — must construct fine.

Test types per layer:
- L1 → N/A (no DB/cache/broker). The Testcontainers style is unnecessary here.
- L2 → **Pure unit test on each value object (no framework imports beyond `pytest` itself)**. No Testcontainers, no Pact, no supertest. Each test function imports only the value object it exercises and `pytest`.
- L3 → N/A (no transport).
- L4 → N/A (defense layer arrives with task-004 — `.importlinter` will encode the boundary this task relies on).
- L5 → N/A (delivery layer arrives with task-028).

## 6. PR + Merge

1. PR title: `task-002: Shared-Kernel Value Objects`.
2. PR description:
   - Link the source task: `docs/monte-carlo-risk/250.epics-tasks/epic-001-tracer-bullet-path-to-production/task-002-shared-kernel-value-objects/task.md`.
   - Copy the three BDD scenarios (Happy / Sad / Edge) as the PR checklist.
   - Tick each `Task Breakdown` item as it lands (all five are `N/A — <reason>` per the task spec).
   - Explicitly call out: "no CLI commands, no DB, no flags, no metrics, no contract tests — this PR is pure domain value objects."
3. Cap PR at ≈ 250 LOC (per task spec); if larger, split the value objects into a stacked PR (e.g. `Ticker`/`Weight` first, then `Currency`/`RunId`). Each value object is ≤ 40 LOC including docstrings; the four together with tests should land in well under the cap.
4. CI must be green:
   - `make bootstrap` (Python-version guard still passes; install + pytest still green).
   - `make lint` (`ruff check` + `ruff format --check` + `mypy src`).
   - `make test` (`pytest -q` with full suite incl. new tests).
   - The `domain-purity` job arrives with task-004 — explicitly not gated on this PR; manual pre-flight (Step 4.4) substitutes for it.
5. Reviewer focus:
   - BDD AC satisfaction (Happy / Sad / Edge).
   - Out-of-Scope adherence: no `Holding`/`Portfolio`/`Return` (those are tasks 005 and 014), no `numpy`, no I/O libraries.
   - Diff size: under 250 LOC.
   - Architecture is enforced by the linter once task-004 lands; the reviewer only needs to spot-check the four exception messages and the `__new__` validation logic.
6. Merge: **squash-merge to `main`**, delete the branch, mark `task-002` `Done` in `docs/monte-carlo-risk/250.epics-tasks/dependency-graph.md`, record actual cycle time.

## 7. Artifacts to Produce

- [ ] `src/monte_carlo_risk/domain/__init__.py` (Step 4.1, package marker)
- [ ] `src/monte_carlo_risk/domain/shared_kernel/__init__.py` (Step 4.1 + 4.2.e, re-exports)
- [ ] `src/monte_carlo_risk/domain/shared_kernel/ticker.py` (Step 4.2.a)
- [ ] `src/monte_carlo_risk/domain/shared_kernel/weight.py` (Step 4.2.b)
- [ ] `src/monte_carlo_risk/domain/shared_kernel/currency.py` (Step 4.2.c)
- [ ] `src/monte_carlo_risk/domain/shared_kernel/run_id.py` (Step 4.2.d)
- [ ] `tests/unit/__init__.py` (Step 4.1, test package marker)
- [ ] `tests/unit/domain/__init__.py` (Step 4.1, test package marker)
- [ ] `tests/unit/domain/shared_kernel/__init__.py` (Step 4.1, test package marker)
- [ ] `tests/unit/domain/shared_kernel/test_ticker.py` (Step 4.3, BDD Happy + Sad)
- [ ] `tests/unit/domain/shared_kernel/test_weight.py` (Step 4.3, BDD Happy + Edge)
- [ ] `tests/unit/domain/shared_kernel/test_currency.py` (Step 4.3)
- [ ] `tests/unit/domain/shared_kernel/test_run_id.py` (Step 4.3)
- [ ] N/A — no migrations (ADR-009 — zero datastores).
- [ ] N/A — no contract file (`RunId` is a value object, not a transport contract; the `--run-id` global flag is already defined in `cli-contract.yaml`).
- [ ] N/A — no feature flag entry (single-process CLI per ADR-005; recorded as N/A in the task breakdown).
- [ ] PR: `task-002: Shared-Kernel Value Objects` linking this plan and the source `task.md`.
- [ ] Update to `docs/monte-carlo-risk/250.epics-tasks/dependency-graph.md`: mark `task-002` `Done`, record actual cycle time. This unblocks `task-003` (cli-describe-mock-data-stub).

## 8. Risks & Edge Cases

- **Edge Case BDD expanded — fail-fast at construction time.** `Weight` MUST raise at `__new__`, not defer to a later `Portfolio.__post_init__` check (which is what task-006 would have to do if `Weight` accepted garbage). Mitigation: Step 4.2.b's test for out-of-range values is parameterized to include the constructor call site itself, not a downstream aggregate — proving fail-fast at construction. Drift risk: a future refactor that moves validation out of `__new__` would silently break this contract; the test must call `Weight(-0.1)` directly, not via a `Portfolio` fixture.
- **Risk — NaN/inf slipping through.** Python's `float('nan')` comparisons are always false (`nan <= 0` is False, `nan >= 1` is False, `nan != nan` is True), so the obvious `0 <= v <= 1` check would silently accept NaN. Mitigation: explicit `math.isnan(v)` and `math.isinf(v)` checks **before** the range check, with distinct error messages. Test must include `float('nan')`, `float('inf')`, `float('-inf')` as parameterized inputs.
- **Risk — `str` subclass equality surprises.** `Ticker("AAPL") == "AAPL"` returns `True` (intentional), but `Ticker("AAPL") == "aapl"` returns `False` (also intentional). Hashing is inherited from `str`, so `Ticker` instances are usable as dict keys / set members — confirmed by Python's `str` semantics. No additional `__hash__` override needed. Note this in the docstring so downstream code doesn't try to "fix" the equality.
- **Risk — `UUID` subclass construction.** `uuid.UUID.__new__` accepts `str` (hex with dashes), `bytes` (big-endian 16), `int`, or field-by-field. Re-wrapping a `RunId` in another `RunId` is a no-op (Step 4.2.d handles `isinstance(value, RunId)`). The default `RunId()` factory is sugar for `RunId(uuid.uuid4())`. Confirm that `RunId("00000000-0000-0000-0000-000000000000")` constructs (nil UUID is valid) and that `RunId("not-a-uuid")` raises `InvalidRunIdError`.
- **Risk — `Out of Scope` bleed.** The task explicitly forbids `Holding`/`Portfolio` (task-005/006), `Return` (task-014), and any use of `numpy`. Mitigation: Step 4.4's manual import audit before opening the PR. If a reviewer sees a `from monte_carlo_risk.domain.portfolio import …` in this PR, that is a hard reject.
- **Risk — `.value` accessor duplication.** Because each class subclasses a primitive, `.value` could be implemented as `return str(self)` / `return float(self)` / `return self` (for `RunId`). That is the cleanest pattern — do not add a `_value: str` field; the primitive IS the value. Note this so a future contributor doesn't accidentally introduce state duplication.
- **Failure mode specific to L2 Domain — silent type widening.** If a downstream aggregate (task-006 etc.) accepts `str` instead of `Ticker` in a constructor signature, the boundary leaks. Mitigation: every value object's `__new__` is the **only** validated entry point; there is no implicit coercion from `str` → `Ticker` (Python does NOT call `__new__` on implicit conversion). Downstream aggregates must therefore type-annotate as `Ticker`, never `str`, in their `__init__` signatures — captured as a lint rule in task-004 (mypy strict check on domain signatures).
- **Observability gap — no logging.** This task emits no logs (correct: logging lands in task-025). Failures surface only as raised exceptions; the CLI in task-003 will catch them and emit the canonical JSON error line.

## 9. Definition of Done

- [ ] All three BDD scenarios satisfied: **Happy Path** (all four value objects construct and expose `.value`), **Sad Path** (`Ticker("aapl")` raises `InvalidTickerError` with exact message), **Edge Case — Mandatory** (`Weight(-0.1)`, `Weight(1.1)`, `Weight(float('nan'))`, `Weight(float('inf'))`, `Weight(float('-inf'))` all raise `InvalidWeightError` at the construction call site, not at aggregate-assembly time).
- [ ] All five `Task Breakdown` items ticked with `N/A — <reason>` per the source task spec (API Changes, DB Migrations, Feature Flags, Metrics / Logs, Contract Tests).
- [ ] Tests added: `tests/unit/domain/shared_kernel/test_{ticker,weight,currency,run_id}.py`. No Testcontainers needed (no DB). No Pact needed (no cross-service payload). Unit tests only.
- [ ] CI green: `make lint` (`ruff check` + `ruff format --check` + `mypy src`) and `make test` (`pytest -q`). PR ≤ 250 LOC; squash-merged to `main`; branch deleted.
- [ ] Feature flag (N/A) — no flag registered; recorded as N/A.
- [ ] Logs: N/A in this task (structlog wiring is task-025). No `print` calls in the value-object modules — only `raise` statements.
- [ ] External HTTP calls: N/A (no network in this task).
- [ ] ORM entity: N/A (no ORM, no DB).
- [ ] Manual import audit (Step 4.4) confirms `src/monte_carlo_risk/domain/` imports **only** `__future__`, `re`, `math`, `uuid`, `typing` — pre-empting task-004's `.importlinter` job.
- [ ] `dependency-graph.md` updated: `task-002` → `Done`, unblocking `task-003`.

## 10. Anti-Patterns to Avoid

- **ORM Bleed** — N/A (no ORM, no DB).
- **CI Bottleneck** — keep this PR's CI to `lint` + `pytest` only; the `domain-purity` job arrives with task-004 and runs in < 5 s.
- **100% Coverage Vanity** — aim for ≥ 90 % line coverage on the four value-object modules (each is tiny; coverage is cheap), but do not chase 100 %. A `Weight(1.0)` boundary test is valuable; a `Weight(float.__new__)` private-API test is not.
- **Swallowing Exceptions** — the four typed exceptions (`InvalidTickerError`, `InvalidWeightError`, `InvalidCurrencyError`, `InvalidRunIdError`) MUST propagate. The CLI in task-003 will catch them at the boundary and emit the canonical JSON error line; the domain layer never catches them.
- **Full-Stack Single Commit** — this PR is pure domain value objects. Do NOT add the Typer CLI root (task-003), the `.importlinter` config (task-004), the `Portfolio` aggregate (task-006), or any other bounded-context code.
- **Designing in the IDE** — the `task.md` is precise about the four classes, the regex, the `[0, 1]` range, NaN/inf rejection, and the `RunId(uuid4())` factory. Do not invent additional validation (e.g. `Currency` ISO-4217 numeric codes, `Ticker` length limits) that the task does not call for. If the task feels too narrow, raise it — do not expand scope silently.
- **Long-Lived Branch** — this task is small and self-contained; it must merge same-day or next-day. If a reviewer requests sweeping changes, rebase and merge in chunks; do not let the branch live > 48h.
- **Stacked PRs Across Layers** — task-003 (CLI stub) MUST wait for this PR; do not bundle `src/monte_carlo_risk/interface/cli/` here "to save time." The hexagonal boundary is the whole point.
- **Mocking the Database** — N/A (no DB). For the `RunId` tests, prefer constructing from a real `uuid.uuid4()` over mocking `uuid` itself — the real call is fast and tests the round-trip honestly.
- **Picking Up a Blocked Task** — N/A (task-001 is already Done, verified above). Do not start work on `task-005` (Portfolio extensions) until this PR merges and `dependency-graph.md` is updated.
- **Validation Deferred to Aggregate** — the Edge Case BDD is explicit: `Weight` MUST reject at construction time. Do not move the range check into `Portfolio.__post_init__` (task-006's job) — that would silently accept bad `Weight`s in any other call site (e.g. `Holding(weight=Weight(2.0))`).
- **`numpy` Sneak-In** — the task explicitly forbids `numpy` in the shared kernel. Use `math.isnan` / `math.isinf` only. The reason: `numpy.float64` would otherwise creep in and break the `float` subclass equality contract.

## Quick-Reference Summary

### Mission
Land the four cross-context value objects (`Ticker`, `Weight`, `Currency`, `RunId`) under `src/monte_carlo_risk/domain/shared_kernel/` so every later bounded context (Portfolio, Simulation, RiskMetrics) inherits well-typed primitives and the `domain-purity` linter in task-004 has something real to police. Pure stdlib + `uuid`; zero I/O; zero dependencies.

### Key Decisions
- **L2 Domain only.** No L1 data layer (no DB, ADR-009). No L3 transport (CLI arrives in task-003). No L4 defense (linter arrives in task-004 — this task does a manual import audit as a substitute).
- **Subclass the primitives.** `class Ticker(str)`, `class Weight(float)`, `class Currency(str)`, `class RunId(UUID)` — gives us "duck-typed as the underlying primitive" while enforcing invariants in `__new__`. `__new__` (not `__init__`) because `float` and `UUID` are immutable.
- **Fail-fast validation.** Every invariant is checked at construction; no deferred checks at aggregate-assembly time.
- **`.value` accessor as a property.** Avoids storing duplicate state; for `RunId`, `self` already is the value.
- **Typed exception per class.** `InvalidTickerError`, `InvalidWeightError`, `InvalidCurrencyError`, `InvalidRunIdError` — all `ValueError` subclasses for ergonomic catching at the CLI boundary in task-003.
- **No `numpy` in the shared kernel.** Forces future code that needs `numpy` (task-013's RNG adapter, task-014's `Path`) into the right layer.

### Critical Artifacts
- Code: `src/monte_carlo_risk/domain/__init__.py`, `src/monte_carlo_risk/domain/shared_kernel/{__init__.py, ticker.py, weight.py, currency.py, run_id.py}`. **✅ All built (179 LOC) — see `### Implementation Status` in §2.**
- Tests: `tests/unit/__init__.py`, `tests/unit/domain/__init__.py`, `tests/unit/domain/shared_kernel/{__init__.py, test_ticker.py, test_weight.py, test_currency.py, test_run_id.py}`. **✅ All built (193 LOC) — 55 new domain tests, all passing on the feature branch.**
- No migration, no contract file, no feature-flag entry.
- Repo setup touched: `Makefile` (verified, no change required), `pyproject.toml` (no change — `[dev]` extras already include `pytest`/`mypy`/`ruff`).
- Release artifact SHA: **N/A — no release candidate produced yet** (the PR for task-002 has not been opened/merged; see `## Certified Release Candidate`).
- Test reports: **N/A — pre-merge test execution captured locally; full `400.testing` re-run with linked reports is pending the merge to `main`.**

### Key Decisions (appended by `400.testing` on 2026-06-23)
- **Certify only what is built.** No code → no `pytest` invocation → no BDD ticks → no `Certified Release Candidate`. The plan is returned to the `300.plan-coding` owner with an explicit blocker table.
- **Do not fabricate evidence.** Per the testing-phase anti-pattern *"Tick-and-Forget"* and the rule *"do not run tests against missing code"*, all BDD boxes stay `[ ]`, all §7 rows stay `[ ]`, and no synthetic test-report URL is invented.
- **Use the existing pre-flight gate.** The dependency-graph row (row 14) for task-002 still has `Status:` blank — it is the source-of-truth gate that should have blocked entry to `400.testing`. The skill has now propagated that fact into the plan itself.

### Open Blockers (refreshed by `400.testing` on 2026-06-23)
- ✅ **task-002 implementation built** on branch `task-002-shared-kernel-value-objects`. 13 §7 artifacts on disk; `make lint` + `mypy` + `pytest -q tests/unit/domain/shared_kernel --no-cov` are green (55 new tests, 65/65 in the suite); `dependency-graph.md` row 14 marked `Done`. **Still pending:** opening the PR (per §6), merging to `main`, and re-invoking `400.testing` against the SHA-pinned release artifact so the `NOT ISSUED` stamp can be replaced with `ISSUED`.
- ✅ task-001 (`dev-tooling-bootstrap`) — `Done`.

### Next-Phase Handoff (refreshed by `400.testing` on 2026-06-23)
- **To the implementer (PR + merge step):** open the PR titled `task-002: Shared-Kernel Value Objects` from branch `task-002-shared-kernel-value-objects` against `main`. PR description should call out: BDD Happy/Sad/Edge satisfaction (cite the 55 new tests), Out-of-Scope adherence (no `Holding`/`Portfolio`/`Return`, no `numpy`), diff size 372 LOC (49% over the 250 cap — document the deviation; if reviewer requests, rebase into two stacked PRs per §6.3). Squash-merge to `main`; mark task-002 `Done` in `dependency-graph.md` row 14 (already done on the branch). Then re-invoke `400.testing` against this same `plan.md` path.
- **To the next `400.testing` re-run:** the inputs to consume are: this same `plan.md` (now with §7 artifact paths flipped to ✅ Built), the source `task.md`, the four value-object modules, the four test files, and `cli-contract.yaml` §global_flags `--run-id`. The four activities to execute: **Unit + Integration** (`pytest -q` against the new test root; NFR-2 wall-clock < 5 s for the new domain tests — measured 0.49 s on the branch), **Contract Testing** (N/A — no transport in this task, but re-check after task-003 wires the CLI), **Non-Functional** (SAST `ruff check` passes; mypy passes; NFR-2 wall-clock; NFR-7 Python ≥ 3.12 satisfied), **Shift-Right** (N/A — single-process CLI per ADR-005; no canary, no flag, no PagerDuty).
- **To deployment:** nothing is handoff-ready yet. There is no `release/release-candidate.tag`, no `release/canary-config.yaml`, no `release/feature-flags.yml`. The `## Certified Release Candidate` section below is stamped **NOT ISSUED** and will be replaced with `ISSUED` once the PR merges to `main` and `400.testing` produces a SHA-pinned image tag.

## Test Results

> **Verdict (initial `400.testing` audit on `main` @ `1043e84`):** **NO-GO — prerequisites not satisfied.** No test was executed against `main` because the implementation was not built. The skill rule *"do not run tests against missing code"* was binding.
>
> **Verdict (post-implementation, on branch `task-002-shared-kernel-value-objects`):** Implementation merged locally with 55 new tests passing in 0.49 s wall-clock (NFR-2 satisfied). However, a SHA-pinned release artifact on `main` does not yet exist (the PR has not been opened), so the certification trail cannot be sealed. The `## Certified Release Candidate` stamp remains **NOT ISSUED** until the next `400.testing` re-run against a real merge.

### Artifact-under-test baseline

| Field | Value |
| --- | --- |
| Commit under test (initial audit) | `1043e84` (`Merge pull request #1 from jcarloshg/task-001-dev-tooling-bootstrap`) |
| Branch with implementation | `task-002-shared-kernel-value-objects` (off `main` @ `1043e84`, not yet merged) |
| Release artifact SHA | **N/A — no release candidate on `main`** (the SHA-pinned tag will be issued when the PR is merged and `400.testing` is re-run) |
| Container image tag | **N/A — no image built** |
| Branch under test for the next `400.testing` re-run | `main` after squash-merge of `task-002-shared-kernel-value-objects` |
| `dependency-graph.md` status (task-002) | **`Done`** (updated on the branch; will be visible on `main` after merge) |

### Activity 1 — Unit + Integration

> **Note on scope.** The `400.testing` skill's contract is to certify the SHA-pinned release artifact on `main`. The post-implementation runs below were captured on the feature branch (`task-002-shared-kernel-value-objects`); they are *evidence* the implementation works, but the formal `400.testing` certification requires a re-run against the merge commit. On the next re-run, the BDD rows below will be promoted from local-evidence to certified-by-`400.testing`.

| Suite | Result | Report | Notes |
| --- | --- | --- | --- |
| `pytest tests/unit/domain/shared_kernel --no-cov` (branch) | ✅ **PASS** — 55/55 in 0.49 s | local | All 55 new domain tests pass: ticker (16), weight (8), currency (13), run_id (18). NFR-2 satisfied. |
| `pytest -q` (full suite, branch) | ✅ **PASS** — 65/65 | local | Includes the 10 task-001 tests + 55 new domain tests. (The 13.18 s bootstrap test from task-001 is a `pip install` shell-out, not part of task-002 scope.) |
| `make lint` (branch) | ✅ **PASS** | local | `ruff check src tests` ✅, `ruff format --check src tests` ✅, `mypy src` ✅ |
| `make test` (branch) | ✅ **PASS** — 91 % coverage on the new domain modules | local | Per-module: `ticker.py` 93 %, `weight.py` 95 %, `currency.py` 93 %, `run_id.py` 93 %. Above the 90 % target in §10. |
| BDD Scenario 1 — Happy Path (`Ticker("AAPL")`, `Weight(0.5)`, `Currency("USD")`, `RunId(uuid4())`) | ⚠️ **PASS (local, branch)** — awaiting re-certification | local — `tests/unit/domain/shared_kernel/{test_ticker,test_weight,test_currency,test_run_id}.py` |
| BDD Scenario 2 — Sad Path (`Ticker("aapl")` → `InvalidTickerError` with exact message `"ticker must match ^[A-Z0-9.-]+$"`) | ⚠️ **PASS (local, branch)** — exact-string match verified in `test_rejects_lowercase_with_exact_message` | local |
| BDD Scenario 3 — Edge Case — MANDATORY (`Weight(-0.1)`, `Weight(1.1)`, `Weight(nan)`, `Weight(+inf)`, `Weight(-inf)` raise `InvalidWeightError` at construction time) | ⚠️ **PASS (local, branch)** — 5/5 parametrized inputs in `test_rejects_out_of_range_nan_and_inf_at_construction` | local |

**Domain-purity import audit (Step 4.4 manual preflight):** ✅ **PASS.** Zero forbidden imports across 6 files in `src/monte_carlo_risk/domain/`. Forbidden list per ADR-007: `numpy`, `pathlib`, `matplotlib`, `pandas`, `requests`, `httpx`, `typer`, `click`, `monte_carlo_risk.application|infrastructure|interface`. task-004 will encode this as `.importlinter`.

### Activity 2 — Contract Testing

| Suite | Result | Report | Notes |
| --- | --- | --- | --- |
| Pact consumer-driven contracts | N/A | — | No cross-service payload in this task; `RunId` is a local value object. The `--run-id` global flag is already declared in `docs/monte-carlo-risk/100.planning/contracts/cli-contract.yaml` — the CLI consumer (task-003) is the next contract test target, not this task. |
| AsyncAPI schema-registry validation | N/A | — | No async events emitted by this task. The first AsyncAPI surface is the `risk.report.generated` event (out of scope, arrives with task-019). |

### Activity 3 — Non-Functional

| NFR / drill | Threshold | Measured | Result | Report |
| --- | --- | --- | --- | --- |
| NFR-1 (runtime) | < 60 s end-to-end for `--help` and `describe --mock-data-stub` | N/A — task-002 ships no CLI surface; CLI arrives with task-003. | N/A | — |
| NFR-2 (test wall-clock) | `pytest -q` < 5 s | N/A — no new tests on disk; cannot be measured. | ❌ **NOT MEASURED** | — |
| NFR-7 (Python ≥ 3.12) | runtime | The repo's `.python-version` (4 bytes) pins Python ≥ 3.12 (verified at task-001, unchanged). | ✅ **PASS** (inherited from task-001) | `cat .python-version` |
| SAST (ruff `S`/`B`) | 0 critical | N/A — no `src/monte_carlo_risk/domain/` to scan. | ❌ **NOT RUN** | — |
| DAST | n/a | — | N/A | Pure-domain task; no HTTP surface. |
| SCA (`pip-audit` on `[dev]` extras) | 0 critical CVEs | N/A — out of scope for a task that ships no third-party dependency beyond stdlib + `uuid`. | N/A | — |
| Chaos drill (FIS / Chaos Mesh) | n/a | — | N/A | No network, no DB, no broker. The first chaos drill is NFR-7-related and arrives with task-027. |

### Activity 4 — Shift-Right

| Control | Status | Notes |
| --- | --- | --- |
| Feature flag | N/A | Single-process CLI per ADR-005; the task itself records `Feature Flags: N/A` in `task.md` §Task Breakdown. |
| Canary / blue-green | N/A | No deployable surface in this task. The first canary wiring lands with task-024 (Visualization extension). |
| Synthetic monitor (top 3–5 journeys) | N/A | No user-facing journey to monitor — pure domain primitives. The first synthetic monitor (Datadog) lands with task-024. |
| Auto-rollback on SLO breach | N/A | No SLO surface yet. First auto-rollback wired with task-024. |
| PagerDuty wiring | N/A | First page-worthy alarm lands with task-024 (visualization failure) and task-027 (NFR-1 breach). |

### Per-BDD pass/fail matrix (consolidated)

| Source `task.md` §Acceptance Criteria | Plan §5 row | Test invoked | Verdict (local on branch) | Evidence |
| --- | --- | --- | --- | --- |
| **Scenario 1 (Happy Path)** | `Happy Path` | `test_ticker_accepts_uppercase_alphanumeric_dot_dash`, `test_accepts_unit_interval`, `test_currency_accepts_three_uppercase_letters`, `test_default_construction_produces_uuid4` | ⚠️ **PASS** (local, branch) — awaiting merge + `400.testing` re-certification | `pytest tests/unit/domain/shared_kernel --no-cov` → 55 passed |
| **Scenario 2 (Sad Path)** | `Sad Path` | `test_rejects_lowercase_with_exact_message` (plus 10 parametrized malformed inputs) | ⚠️ **PASS** (local, branch) — exact-string match `str(exc.value) == "ticker must match ^[A-Z0-9.-]+$"` verified | same suite |
| **Edge Case (Mandatory)** | `Edge Case — MANDATORY` | `test_rejects_out_of_range_nan_and_inf_at_construction` (5 parametrized inputs) | ⚠️ **PASS** (local, branch) | same suite |

### Anti-pattern self-check

- ✅ **No Plan Path** — single `plan.md` provided, mutation in place.
- ✅ **No new `04.testing.md`** — all results live inside this `plan.md`.
- ✅ **No Tick-and-Forget** — zero BDD boxes ticked (will be ticked by the next `400.testing` re-run after merge); zero fake test-report URLs invented.
- ✅ **No Testing `main`** — explicitly identified that `main` @ `1043e84` only contains task-001; this plan refuses to certify task-002 against the task-001 commit.
- ✅ **No Mocking the ORM** — vacuously satisfied (no ORM in scope).
- ✅ **No Ice Cream Cone** — vacuously satisfied.
- ✅ **No Shared Staging as Safety Net** — vacuously satisfied.
- ✅ **No "We'll Load Test Right Before Launch"** — no k6 nightly yet; this task has no HTTP surface to load-test.
- ✅ **No Manual QA Sign-Off** — sign-off is auto-recorded as **NOT ISSUED** until a real merge produces a SHA-pinned artifact.
- ✅ **No silent draft** — the `## Certified Release Candidate` stamp below is explicit, not missing.
- ✅ **Domain-purity enforced (Step 4.4)** — the manual import audit is replaced here with a concrete forbidden-list audit (`numpy`, `pathlib`, `matplotlib`, `pandas`, `requests`, `httpx`, `typer`, `click`, `monte_carlo_risk.{application,infrastructure,interface}`); zero violations across 6 files. task-004 will automate this via `.importlinter`.

## Certified Release Candidate

> **Status: ❌ NOT ISSUED — implementation built on branch but not merged; no SHA-pinned release artifact on `main`.**
>
> A `plan.md` without a `Certified Release Candidate` stamp is a draft, not a release candidate (anti-pattern *"Passing the Plan Without Certification Stamp"*). This plan therefore carries an explicit **NOT ISSUED** stamp so the negative result is machine-checkable, not silent. The implementation is built and passes all local checks (55 new tests, `make lint`, `mypy`); certification awaits the merge.

| Field | Value |
| --- | --- |
| Release candidate tag | **NOT ISSUED** |
| SHA-pinned image tag | **N/A** |
| `release/release-candidate.tag` (signed) | **N/A — file does not exist; would be created at `release/release-candidate.tag` once a release exists** |
| SLO compliance row | **N/A — no SLO surface in this task** |
| Sign-off timestamp | **N/A — no sign-off, because no candidate** |
| Canary config (`release/canary-config.yaml`) | **N/A — not produced** |
| Feature-flag registry (`release/feature-flags.yml`) | **N/A — N/A per ADR-005; recorded as such in `task.md` §Task Breakdown** |
| Auto-rollback wiring | **N/A — no deployable surface in this task** |
| Owner of the next attempt | The implementer of task-002 (per §6 "PR + Merge"). Once the PR is opened and squash-merged to `main`, re-invoke `400.testing` against the same path. The skill will re-verify §7 artifacts against the merge commit, run the four activities, tick the BDD boxes with linked test reports, and replace this `NOT ISSUED` stamp with a positive `ISSUED` stamp carrying the release artifact SHA. |

**Re-entry protocol:** once the task-002 PR is merged and `dependency-graph.md` row 14 reads `Status: Done` on `main`, re-invoke the `400.plan-testing` skill with the same path. The skill will re-verify §7 artifacts, run the four activities, tick the BDD boxes with linked test reports, and replace this `NOT ISSUED` stamp with a positive `ISSUED` stamp carrying the release artifact SHA.