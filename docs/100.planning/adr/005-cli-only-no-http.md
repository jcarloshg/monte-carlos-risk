# ADR-005 — CLI is the Only Interface in v1 (No HTTP API)

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Source inputs:** `docs/00.defining.md` Q2.1, Q5.x, README note #1

## Context

The user interface for this project is a single command (`docker compose up`)
that runs a simulation and writes PNG + JSON outputs. The defining doc is
explicit that there is no UI, no admin, and no end-user distinction
(Defining Q5.1). We need to decide whether to also expose an HTTP API.

## Options Considered

1. **HTTP API (FastAPI / Flask).** Production-shaped. Adds an ASGI server,
   an OpenAPI generator, a request-validation layer, and a deployment story.
   Also requires a new bounded context seam (the `interfaces/http/`
   directory) and CORS/auth decisions for a local-only tool.
2. **CLI only.** Click/Typer command surface. Frozen in
   `task/monte-carlos-risk/100.planning/contracts/openapi.yaml` (a CLI-
   surface doc, not a true OpenAPI; full justification below).

## Decision

**Option 2.** The CLI is the only v1 interface. The
`contracts/openapi.yaml` file documents the CLI command surface (subcommands,
flags, exit codes) in a YAML structure that mirrors OpenAPI 3.1's
`paths:` schema, so a future REST surface can be added by converting each
CLI command to an HTTP route with the same `operationId`. Exit codes map
1-to-1 to HTTP status codes (1→500, 2→422, 3→404, 4→503, 5→500, 6→500).

A REST API is explicitly out of scope for v1; introducing it later is
non-breaking because the CLI surface remains.

## Consequences

**Positive**
- One command runs everything. Matches the README contract.
- No server, no port, no auth surface.
- Output is files-on-disk, which the author already knows how to inspect.

**Negative**
- No multi-user / concurrent runs in v1. Acceptable — Defining Q2.1 says
  DAU = 1.
- Future REST surface will be an additive port (no schema migration on the
  CLI side).

**Reversibility**
- Reversible by adding `src/interfaces/http/` with a FastAPI app that
  delegates to the same `application/` use cases. The CLI stays.
