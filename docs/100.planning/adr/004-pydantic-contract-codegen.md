# ADR-004 — Pydantic v2 as Source of Truth; JSON Schema Generated via Codegen

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Source inputs:** `docs/00.defining.md` 300-Q4.1, 300-Q4.3, 300-Q8.6

## Context

Inputs (portfolio JSON, simulation profile JSON) and outputs (event payloads,
metrics JSON) all have rigid shapes. The defining doc requires these to live
in `docs/contracts/` as JSON Schema. We need to choose between hand-writing
schemas (drift-prone) or generating them from code.

## Options Considered

1. **Hand-write JSON Schema.** Author writes and maintains both the Pydantic
   model and the JSON Schema. Two sources of truth; they will drift.
2. **Pydantic v2 is the source; JSON Schema is generated.** `make contracts`
   invokes `pydantic.json_schema()` and writes to `docs/contracts/`. The
   generation runs in CI; the diff is reviewed in the model PR.
3. **JSON Schema is the source; Pydantic is generated.** Less common in
   Python; loses type hints in code.

## Decision

**Option 2.** Pydantic v2 models in `src/domain/` are the source of truth.
The `make contracts` target regenerates all JSON Schemas under
`docs/contracts/` and `task/monte-carlos-risk/100.planning/contracts/` (this
folder is the planning-time frozen snapshot; CI regenerates from current
code into `docs/contracts/`). The CI check fails if a model changed without
a regenerated schema in the same PR.

The frozen planning-time snapshots in `task/.../contracts/` are the
Definition-of-Ready artifacts; the `docs/contracts/` directory is the
always-current, machine-generated equivalent.

## Consequences

**Positive**
- One source of truth (the Pydantic class). `mypy --strict` validates it.
- `docs/contracts/portfolio.schema.json` is always the current shape.
- Adding a field is one-line code change + `make contracts`.

**Negative**
- The `make contracts` step adds 2 s to CI. Negligible.
- Generated JSON Schema is verbose; committed files are large but gitignored
  churn is bounded by the number of model changes per PR.

**Reversibility**
- Fully reversible. Hand-written schemas can replace generated ones later
  if the project outgrows Pydantic.
