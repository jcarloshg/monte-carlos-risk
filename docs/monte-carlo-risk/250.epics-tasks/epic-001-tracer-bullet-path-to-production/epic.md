# Epic 001: Tracer Bullet — Path to Production

**Status:** Ready
**Bounded Context:** (cross-cutting: scaffold)
**Sequence Order:** 1 of 6 (Tracer Bullet — must ship first per Playbook §2.3)
**Estimated Sprints:** 1

> Small business value (one trivial `describe-mock-data` command), but forces the entire vertical slice of infrastructure into existence: pyproject + Docker + CI + hexagonal layout + structlog + canonical error envelope. Every subsequent Epic moves ~10× faster because this Epic ships the path-to-prod.

## 1. Business Context & Value

- **Why are we building this?** A clean `git clone` on any developer machine must produce a working CLI in under five minutes, with a green CI pipeline. Without this, every later Epic pays the same bootstrap tax.
- **Success Metrics:**
  - `git clone … && make bootstrap && make test` exits 0 on a clean Linux/macOS machine in **≤ 5 minutes**.
  - `docker compose run --rm monte-carlo describe-mock-data` exits 0 and prints a JSON document matching `mock_data_descriptor` in `100.planning/contracts/cli-contract.yaml`.
  - The CI workflow at `.github/workflows/ci.yml` has 4 green jobs: `lint`, `domain-purity`, `test`, `docker-smoke`.

## 2. Architectural Scope (C4 Level 2)

- **Containers Touched:** `cli` (Typer root), the composition root (`interface/cli/app.py`), the error envelope (`interface/errors.py`), the logging setup (`interface/logging.py`).
- **External Dependencies:** None. The Tracer Bullet does NOT bundle the mock CSV corpus yet — that is Epic 003 / task-010. The `describe-mock-data` command returns a stub JSON with hardcoded metadata.
- **Database Impact:** None (ADR-009 — zero datastores).

## 3. Strict "Out of Scope"

- **Bundled mock CSV corpus** — Epic 003 / task-010.
- **Simulation, RiskMetrics, Visualization contexts** — Epics 003, 004, 005.
- **`simulate` command** — Epic 003 / task-016 (Tracer Bullet only ships a stub that emits a `PortfolioDefined` event then exits cleanly).
- **`validate-portfolio` command** — Epic 002.
- **Real market-data adapter (`HttpMarketDataSource`)** — v2, gated by Spike S-001.
- **Cloud deployment / production rollout** — single-process educational tool, $0/mo budget.

## 4. Non-Functional Requirements (NFRs)

All traceable to `100.planning/01.planning.md` §2.

- **NFR-2** (test suite budget): full unit suite ≤ 5 s; CI total ≤ 5 min including Docker build.
- **NFR-3** (domain purity): `.importlinter` passes with zero violations.
- **NFR-6** (error contract): every CLI failure in this Epic emits exactly one canonical JSON error line matching `error_schema` in `cli-contract.yaml`.
- **NFR-7** (one-command bootstrap): `make bootstrap` succeeds on a clean machine.

## 5. Required Technical Artifacts (Definition of Ready)

- [ ] C4 Container Diagram approved. ✅ Adopted from `100.planning/diagrams/c4-container.md`.
- [ ] OpenAPI/Swagger contract merged. **N/A — CLI-only per ADR-005; substitute `100.planning/contracts/cli-contract.yaml` is approved.**
- [ ] UI/UX Figma designs approved (including error states). **N/A — CLI-only per ADR-005; no UI surface.**
- [ ] Event schemas merged. ✅ `100.planning/contracts/events.schema.json` is approved.
- [ ] Hexagonal package layout approved. ✅ `200.designing/adr/007-hexagonal-package-layout.md`.
- [ ] Linter contract approved. ✅ `200.designing/architecture/hexagonal.md` §Linter Contract.

## 6. User Stories (BDD)

- **Story 1.1:** Bootstrap a clean clone to a green pipeline in ≤ 5 minutes.
  - *Scenario:* `Given` a fresh git clone on a Linux/macOS machine with Docker installed, `When` I run `make bootstrap && make test`, `Then` the project is set up, all tests pass, and `make lint` exits 0 within 5 minutes.
  - *Edge Case placeholder:* handled in `task-001`.
- **Story 1.2:** Run the trivial `describe-mock-data` command via Docker and receive valid JSON on stdout.
  - *Scenario:* `Given` the Docker image is built, `When` I run `docker compose run --rm monte-carlo describe-mock-data`, `Then` exit code is 0 and stdout is a JSON document matching `mock_data_descriptor` schema.
  - *Edge Case placeholder:* handled in `task-003`.
- **Story 1.3:** CI catches a forbidden import in `domain/`.
  - *Scenario:* `Given` a PR that adds `import matplotlib` inside `src/monte_carlo_risk/domain/`, `When` CI runs, `Then` the `domain-purity` job fails with a clear error pointing to the offending line.
  - *Edge Case placeholder:* handled in `task-004`.
