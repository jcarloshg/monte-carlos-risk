# Task 023 — `FilesystemOutputWriter` Adapter

**Epic:** epic-005-visualization-render-risk-charts
**Layer:** Infrastructure
**Sprint:** 06
**Depends on:** task-001
**Owner:** jcarloshg
**Estimated PR scope:** 1 PR, ≈ 200 LOC

## Context

Implements the `OutputWriter` Protocol from `application/ports/output_writer.py`. Writes bytes (PNGs from the renderer) and JSON (the `simulation_report`) to a filesystem path. Pre-flight check for writability is mandatory (cheaper than discovering it mid-simulation).

## Acceptance Criteria (BDD)

- [ ] **Scenario 1 (Happy Path):** Given a writable `output_dir`, `When` I call `FilesystemOutputWriter().write_bytes(path, png_bytes)` and `.write_json(path, dict)`, Then the files exist at the given paths and have the expected contents.
- [ ] **Scenario 2 (Sad Path):** Given `output_dir` is read-only, `When` I call `ensure_directory(path)`, Then `OutputDirNotWritableError` is raised with the resolved absolute path in `context`.
- [ ] **Edge Case (Mandatory):** If the parent directory of `path` does not exist, `FilesystemOutputWriter.ensure_directory` MUST create it (idempotent: re-calling on an existing dir is a no-op). A unit test asserts both first-call and re-call behaviors.

## Task Breakdown (Definition of Ready)

- [ ] **API Changes:** N/A.
- [ ] **Database Migrations:** N/A.
- [ ] **Feature Flags:** N/A.
- [ ] **Metrics / Logs:** N/A.
- [ ] **Contract Tests:** Adds `tests/contract/test_output_writer_contract.py` — parameterized against any `OutputWriter`; asserts (a) write succeeds + (b) ensure_directory idempotent + (c) error_code mapping.

## Out of Scope

- The renderer (`task-022`).
- The orchestrator extension (`task-024`).
- S3 / cloud storage writers — N/A per ADR-008 / ADR-009.

## Deliverables

- `src/monte_carlo_risk/infrastructure/filesystem/filesystem_output_writer.py` — `class FilesystemOutputWriter` implementing `OutputWriter`. Uses `pathlib.Path`. `ensure_directory` is idempotent (`mkdir(parents=True, exist_ok=True)`).
- `src/monte_carlo_risk/domain/visualization/exceptions.py` (extend) — `OutputDirNotWritableError`. Note: `cli-contract.yaml` already has `output_dir_not_writable` as an error code.
- `tests/unit/infrastructure/filesystem/test_filesystem_output_writer.py` — happy + sad + idempotent-edge case.
- `tests/contract/test_output_writer_contract.py` — first cross-implementation contract test.
