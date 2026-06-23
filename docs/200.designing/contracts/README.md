# Contracts (Frozen Snapshots, Inherited from Planning)

> Source of truth: `docs/100.planning/contracts/` (Planning, frozen).
> These files are **byte-identical copies** of the Planning-time contracts.
> Per ADR-004 (Pydantic v2 as source of truth; JSON Schema generated via
> codegen), the planning-time contracts are the Definition-of-Ready frozen
> snapshots; the machine-generated, always-current versions live under
> `docs/contracts/` (created by `make contracts`).
>
> The Designing phase does **not** modify the contract surface. Any change
> to a Pydantic model requires regenerating the corresponding JSON Schema
> in the same PR (ADR-010 CI gate).

## Inherited files

| File | Source | Frozen status |
|---|---|---|
| `openapi.yaml` | Planning | Immutable |
| `asyncapi.yaml` | Planning | Immutable |
| `portfolio.schema.json` | Planning | Immutable |
| `simulation_profile.schema.json` | Planning | Immutable |
| `events/envelope.schema.json` | Planning | Immutable |
| `events/simulation_requested.schema.json` | Planning | Immutable |
| `events/returns_loaded.schema.json` | Planning | Immutable |
| `events/path_sampled.schema.json` | Planning | Immutable |
| `events/drawdown_computed.schema.json` | Planning | Immutable |
| `events/risk_metrics_calculated.schema.json` | Planning | Immutable |
| `events/simulation_completed.schema.json` | Planning | Immutable |
| `events/simulation_failed.schema.json` | Planning | Immutable |

## What this folder means for downstream phases

- **Coding (300):** the openapi.yaml and asyncapi.yaml files document the
  CLI surface + the event contract the engine emits. Both are reference
  documentation; the source of truth for runtime shapes is the Pydantic
  models in `src/domain/`.
- **Testing (400):** the JSON Schema files are the inputs the contract
  tests will validate against (`jsonschema.validate` against each
  `events.jsonl` row + each `metrics.json`).
- **Future forks:** if a vendor integration adds a new event type, the
  new event's JSON Schema is added under `events/` with a bumped
  `schemaVersion`, and a new ADR supersedes the old one.