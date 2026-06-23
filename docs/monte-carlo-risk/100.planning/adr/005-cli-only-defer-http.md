# ADR-005 — CLI-Only v1; Defer HTTP Service Surface

- **Status:** Accepted
- **Date:** 2026-06-23
- **Deciders:** jcarloshg
- **Source:** `00.defining.md` §2 Contracts, §3 Sprint Zero & Tooling; `01.planning.md` §4 Deliverables.

## Context

The defining phase selected **CLI only** as the v1 interface (`00.defining.md` §1 Domain & Flow — confirmed in user questions). The CI pipeline builds a Docker image, runs `monte-carlo --help` as a smoke test, and the user interacts with the tool via `docker compose run monte-carlo simulate …`.

The Planning Phase playbook §4 Deliverables lists OpenAPI / AsyncAPI / GraphQL as required frozen contracts. For a CLI-only tool, none of these apply directly.

## Options

1. **Force OpenAPI on the CLI.** Model each CLI command as an "endpoint" with request body = CLI flags and response body = JSON output. Technically possible; semantically misleading; commits the project to a fake HTTP surface that no one consumes.
2. **Produce no contract; rely on `--help` and a `README` section.** Cheapest. But the playbook rejects "living document specifications" and the contract must be **frozen and versioned**, not free-form prose.
3. **Produce a frozen CLI contract (YAML) + JSON Schema for in-process events.** Honest about the actual surfaces; versioned; machine-checkable; revisitable later if a real HTTP surface is added.

## Decision

**Option 3: frozen CLI contract + JSON Schema events.**

- **`contracts/cli-contract.yaml`** defines:
  - Each command (`simulate`, `validate-portfolio`, `describe-mock-data`) as a top-level entry.
  - For each command: the flag schema (name, type, required, default, validation), the stdout JSON schema, the stderr error schema, and the exit-code table.
  - Versioned at `v1.0.0`. Frozen on merge.
- **`contracts/events.schema.json`** defines the JSON Schema for each in-process event payload (`PortfolioDefined`, `MarketDataLoaded`, `SimulationStarted`, `SimulationCompleted`, `RiskMetricsCalculated`, `ChartsRendered`). Versioned at `v1.0.0`.
- **No `openapi.yaml` in v1.** When v2 adds an HTTP service (FastAPI or similar), an OpenAPI spec is produced at that time and references the same event and error schemas.
- **No `asyncapi.yaml` in v1.** When v2 adds a message broker (Kafka / SNS / EventBridge), an AsyncAPI spec is produced then.

## Consequences

**Positive.**
- The contract is honest: it describes what the tool actually exposes, not a hypothetical HTTP surface.
- The CLI contract is machine-checkable: a CI step can launch the CLI with `--help --format json` and diff against the contract.
- Event schemas are reusable: when v2 produces `openapi.yaml` and `asyncapi.yaml`, the schemas are already there.

**Negative.**
- The Planning Phase playbook lists OpenAPI/AsyncAPI as standard artifacts; we deviate. Mitigated by this ADR explicitly justifying the deviation and naming the trigger (an HTTP service being added) that produces them.

**Supersedes.** None.
