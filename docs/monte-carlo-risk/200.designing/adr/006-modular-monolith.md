# ADR-006 — Modular Monolith (Single Python Process); Microservices Explicitly Rejected

- **Status:** Accepted
- **Date:** 2026-06-23
- **Deciders:** jcarloshg
- **Source:** `00.defining.md` §1 Targets & Budget ($0/mo, single user); `01.planning.md` §3 ADRs (especially ADR-005 CLI-only); `02.designing.md` §1.

## Context

The Planning phase established four bounded contexts (`Portfolio`, `Simulation`, `RiskMetrics`, `Visualization`) and a `$0/month` cloud budget (NFR-8). The Design playbook's first macro-architecture rule is *"Default to a Modular Monolith. … Microservices require an ADR justifying the split."*

The question is whether to extract any of the four contexts into a separate process (separate Docker container, separate codebase, separate deployable). Three options were considered.

## Options

1. **True microservices.** Each of the four contexts becomes its own Python package, its own Docker image, its own Git repo, communicating via HTTP (or gRPC, or a message broker). Per the Playbook, this requires a positive justification, not just absence-of-justification-for-monolith.
2. **Modular monolith (in-process modules).** All four contexts live inside one Python package, one Docker image, one process. Communication is in-process method calls; events are value objects passed by reference (not serialized).
3. **Distributed monolith.** True microservices in deployment topology, but synchronous HTTP calls between them such that one user request fans out across 4 services to complete. This is the worst of both worlds — the Playbook explicitly rejects it as an anti-pattern.

## Decision

**Option 2: modular monolith.**

Justification, per NFR-8 and the absence of any distributed-system pressure:

- **$0/month budget.** No managed broker, no service mesh, no Kubernetes, no per-service cloud bill. A monolith on a laptop is free.
- **Single user.** NFR-1 target is `< 1` peak TPS. No horizontal scaling needed; a single Python process on a single core (plus numpy's BLAS threads) handles the default workload well within the latency budget (NFR-1 P50 ≤ 10 s).
- **No cross-team coordination.** There is one developer. Splitting a codebase across multiple repos/processes to be consumed by one developer is pure overhead.
- **Hexagonal seams enable future extraction.** Because Planning ADR-001 mandates strict hexagonal boundaries with `import-linter` enforcement, any one of the four contexts CAN be extracted later by:
  1. Moving the context's package to a new repo.
  2. Replacing the in-process `Protocol` calls with an HTTP/gRPC adapter.
  3. Adding a broker-backed event bus (would supersede ADR-011).
  4. Spinning up a second Docker image.
  The extraction cost is bounded by the size of the context (each is ~hundreds of lines of pure Python); the cost of getting microservices wrong now would be far higher.
- **Microservices without justification is a textbook anti-pattern** (Playbook §Avoid — *"Build It and They Will Come"*). Allocating ops budget, CI complexity, and on-call burden to a system that doesn't need them violates the cost discipline of this project.

## Consequences

**Positive.**
- One Dockerfile, one `docker compose`, one CI pipeline, one test command.
- Single-process debugging — no distributed tracing needed.
- All four contexts share the in-memory state of one run; no serialization overhead between contexts.
- Idempotency (NFR-5) and reproducibility (NFR-4) are properties of one process, not of a choreography of services.

**Negative.**
- Cannot scale individual contexts independently. If `SimulationRun` becomes the bottleneck (unlikely for an educational tool with one user), the entire process must be replicated.
- The orchestrator is a single point of failure. Acceptable because the cost of failure is "re-run the CLI."

**Migration trigger.** A future ADR should re-evaluate this decision if **any** of the following becomes true:
- Monthly budget exceeds ~$50/mo AND the bottleneck is identified in one specific context.
- A second developer joins and wants to own `RiskMetrics` independently.
- An external consumer needs to invoke `Simulation` over HTTP (would supersede ADR-005 too).

**Supersedes.** None.
