# Architecture — Contract Deviations from Playbook Defaults

> Frozen on: 2026-06-23
> Source: Planning ADR-005 (CLI-only v1, defer HTTP); reaffirmed by Design.

The Playbook §Architectural Artifacts lists `contracts/openapi.yaml` and `contracts/asyncapi.yaml` as required Design artifacts. This project produces **neither** in v1. This file is the single source of truth for *why* and *when* they would be produced.

---

## What we have instead

| Playbook default | Our substitute | Where it lives |
|---|---|---|
| `openapi.yaml` | `cli-contract.yaml` — frozen CLI surface (commands, flags, exit codes, JSON schemas, error envelope) | `100.planning/contracts/cli-contract.yaml` |
| `asyncapi.yaml` | `events.schema.json` — frozen JSON Schema for in-process domain events | `100.planning/contracts/events.schema.json` |

Both substitutes are **versioned** (`v1.0.0`), **stored in the repo as code** (YAML and JSON), and **validated in CI** (the CLI's actual `--help` output must match `cli-contract.yaml`; event emission must validate against `events.schema.json`).

---

## Why

The CLI is the only public surface in v1 (ADR-005). OpenAPI's request/response semantics — paths, HTTP methods, status codes, content negotiation — do not apply to a CLI tool. Producing an OpenAPI spec that no one consumes would be a textbook instance of **resume-driven development** (the Playbook's explicit anti-pattern): building the artifact because the playbook says we should, not because the system needs it.

Similarly, AsyncAPI's channel-based messaging model does not apply because there is no message broker. Domain events are **in-process value objects** flowing through direct method calls; their schemas are JSON Schema, not AsyncAPI channels.

---

## When these substitutes become insufficient (i.e., when OpenAPI/AsyncAPI must be produced)

A future trigger requires producing the Playbook-default artifacts:

1. **OpenAPI** must be produced when **either** of these becomes true:
   - An HTTP service surface is added (e.g., a FastAPI app exposing `/simulate` as a POST endpoint). Trigger: ADR accepting this change.
   - A typed client SDK is generated from the contract for an external consumer. Trigger: a third party requests a stable HTTP API.

2. **AsyncAPI** must be produced when **either** of these becomes true:
   - A real message broker is introduced (Kafka, SNS/SQS, EventBridge). Trigger: ADR accepting this change, almost certainly paired with ADR-011 being superseded to add a transactional outbox.
   - Two or more processes need to exchange `monte-carlo-risk` events. Trigger: services are extracted from the monolith (would supersede ADR-006).

When a trigger fires:
1. Re-run the `000.defining` and `100.planning` skills to capture the new business reality.
2. Re-run the `200.designing` skill, which adds `contracts/openapi.yaml` and/or `contracts/asyncapi.yaml` next to the existing `cli-contract.yaml` and `events.schema.json`.
3. The substitutes are **not** deleted — the CLI contract is the source of truth for CLI semantics even after an HTTP surface is added (the HTTP endpoints call into the same use cases).
4. The JSON Schema definitions in `events.schema.json` are **reused** as `$ref` targets from the new OpenAPI/AsyncAPI specs — no schema duplication.

---

## Validation in CI

Until the triggers above fire, CI enforces the substitutes are honored:

- `cli-help-snapshot` job — runs the CLI with every documented flag, captures `--help`, and diffs against a frozen snapshot. Any drift fails the build.
- `events-schema-validation` job — runs a property-based test that invokes `RunSimulation.execute()` with a fixture portfolio, captures every domain event emitted, and validates each against `events.schema.json`.
- `error-schema-snapshot` job — runs the CLI with a deliberately invalid portfolio, captures stderr, parses it as JSON, and validates the single error line against `error_schema.error_code` ∈ enum.

When OpenAPI/AsyncAPI are added, additional CI jobs (`openapi-spec-lint`, `asyncapi-spec-lint`, `dto-generation`) are added alongside.

---

## Cross-references

- Planning ADR-005 — CLI-only v1, defer HTTP (the original justification).
- Design ADR-006 — Modular Monolith (no services means no inter-service contracts).
- `100.planning/contracts/cli-contract.yaml` — the substitute OpenAPI.
- `100.planning/contracts/events.schema.json` — the substitute AsyncAPI.
