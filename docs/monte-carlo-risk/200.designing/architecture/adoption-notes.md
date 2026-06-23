# Adoption Notes — Design Phase Adopts Planning C4 Diagrams Unchanged

> Frozen on: 2026-06-23

The Design playbook §4 lists `diagrams/c4-context.md` and `diagrams/c4-container.md` as required Design artifacts. Both already exist under `100.planning/diagrams/` and are **adopted unchanged** as the Design-phase frozen versions.

## Why adopted unchanged

1. **The Planning C4s already reach container-level detail.** The `c4-container.md` from Planning shows the four bounded contexts as in-process components, the `MarketDataSource` port, and the adapters — which is precisely the level of detail a developer needs to start coding. Adding a Design-phase C4 with the same content would violate the "frozen once merged" principle for architectural diagrams.
2. **The "stop at container" rule is honored.** No component-level UML is added.
3. **No new architectural decisions in Design affect the C4s.** The Design phase added 7 ADRs (006..012) and three architecture docs (`hexagonal.md`, `data-flow.md`, `contract-deviations.md`) — none change the boundary between the system and the outside world (C4 Context) or the boundary between the system and its in-process components (C4 Container).

## Cross-references to Design additions

The C4 Container from Planning shows the **shape** of the system; the Design additions show the **internals**:

- `200.designing/architecture/hexagonal.md` — the concrete directory tree that backs each container in the C4.
- `200.designing/architecture/data-flow.md` — the sequence of method calls that traverses the containers in the C4.
- `200.designing/adr/007-hexagonal-package-layout.md` — the directory tree as an immutable decision.

## Files

- `100.planning/diagrams/c4-context.md` — adopted as the Design-phase C4 Context.
- `100.planning/diagrams/c4-container.md` — adopted as the Design-phase C4 Container.

No new files are produced under `200.designing/diagrams/` for C4. The `db-erd.md` artifact is produced separately because there is no datastore to diagram (see `200.designing/diagrams/db-erd.md`).
