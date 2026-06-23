# ADR-001 — Strict Hexagonal Architecture with `import-linter` Enforcement

- **Status:** Accepted
- **Date:** 2026-06-23
- **Deciders:** jcarloshg
- **Source:** `00.defining.md` §3 Layer Enforcement, §4 Modern Test Pyramid; `01.planning.md` §3 ADRs.

## Context

The project is small (single developer, single CLI process) but the developer explicitly wants Domain-Driven Design "because in the future I want to connect third party API to get more information" (`README.md` line 11). A future `HttpMarketDataSource` must be swappable into a system that today runs entirely on a `MockMarketDataSource` without touching the simulation or risk math.

Two architectural styles are candidates:

- **Layered (loose):** `domain/`, `application/`, `infrastructure/`, `interface/` folders exist by convention only; nothing prevents `domain/` from importing `requests` or `matplotlib`.
- **Hexagonal (strict):** same folder layout, but layer boundaries are machine-enforced. Domain has no compile-time or runtime dependency on infrastructure; ports are first-class.

Without machine enforcement, hexagonal architecture degrades into layered architecture within a single sprint — `domain/` calls `matplotlib.pyplot.hist()` "just this once" and the boundary is gone.

## Options

1. **Layered folders, no enforcement.** Cheapest to set up. Boundaries erode silently.
2. **Hexagonal + manual code review.** Architectural intent documented; reviewers must catch violations. High review burden, low reliability.
3. **Hexagonal + `import-linter` CI job.** Same intent as #2, but violations fail the build before review. The Python ecosystem equivalent of `eslint-plugin-boundaries` / `dependency-cruiser` for JS.

## Decision

**Option 3: hexagonal architecture with `import-linter` enforced in CI.**

The forbidden-import graph:

- `domain/` MAY NOT import from `infrastructure/`, `application/`, `interface/`.
- `domain/` MAY NOT import `pathlib`, `requests`, `matplotlib`, `typer`, `click`, `httpx`, `urllib3`, `aiohttp`.
- `domain/` MAY import `numpy` (see ADR-002), `decimal`, `dataclasses`, `enum`, `typing`, `uuid`, `abc`, `math`, and the Python stdlib primitives.
- `application/` MAY import from `domain/`. MAY NOT import from `infrastructure/` or `interface/` (except for `Protocol` definitions in `application/ports/`).
- `infrastructure/` MAY import from `domain/` and `application/`.
- `interface/` (CLI entrypoint) MAY import from all layers.

The CI job runs `lint-imports` (the `import-linter` CLI) on every push and PR. A violation fails the build.

## Consequences

**Positive.**
- The `HttpMarketDataSource` v2 work cannot accidentally pollute the domain; the lint job will block the PR.
- Refactoring the CLI to a web UI (future) only requires moving the entrypoint; the domain is untouched.
- Test pyramid floor (pure domain unit tests, no I/O) is structurally guaranteed — no need to trust that contributors "remember" not to import `matplotlib`.

**Negative.**
- Adds a dev dependency (`import-linter`) and one CI step (~3 s).
- Contributors must understand the layer rules. Mitigated by ADR-002 and a `CONTRIBUTING.md` example.
- Slightly more boilerplate: ports and adapters require a `Protocol` definition per seam.

**CAP stance.** All four bounded contexts are AP (best-effort, partition-tolerant) by default — there is no replication, no consensus, and no network partition in v1. Consistency collapses to "single-process in-memory state" and needs no further negotiation.

**Supersedes.** None.
