# ADR-016 — Composition Root as Hand-Rolled Factory (No DI Library)

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Supersedes:** none
- **Source inputs:** ADR-002 (hexagonal layout), ADR-015 (Port inventory),
  `docs/200.designing/02.designing.md` §2.2.3

## Context

The Designing playbook (§2.2) calls for "aggressive dependency
injection" and mentions containers like Awilix / Inversify. We need to
decide how dependencies flow from adapters into use cases.

Our system has:

- **5 Ports** (ADR-015).
- **3 Use cases** (`RunMonteCarloSimulation`, `ComparePortfolios`,
  `ReplaySimulation`).
- **2 Container variants** (production + test).

A full DI container library (`dependency-injector`, `pinject`, `inject`,
`kiara`) would add:

- A runtime dependency (and CVE pipeline).
- An XML / YAML / Python decorator config to learn.
- A failure mode where the container can't resolve a dependency at
  startup, far from the call site.
- A scoping model (`@singleton`, `@scoped`) we don't need.

The Pythonic alternative is **constructor injection via dataclasses**:
the composition root at `src/interfaces/cli/main.py` builds a `Container`
dataclass that holds the wired adapters; use cases receive the `Container`
(or just the ports they need) via their `__init__`.

## Options Considered

1. **`dependency-injector` library.** Production-grade. ~600 lines of
   library code; battle-tested in FastAPI / Flask apps.
2. **Hand-rolled composition root** (a `Container` dataclass + factory
   functions). Zero new dependencies. ~50 lines of wiring code.
3. **Module-level singletons** (adapters are module-global). Simplest
   possible. Breaks the import-linter rule (ADR-002) because
   `infrastructure/` would be imported by `application/`.

## Decision

**Option 2.** The composition root lives at
`src/interfaces/cli/main.py` and is a single `Container` dataclass with
two factory functions (`build_production_container` and
`build_test_container`).

```python
# src/interfaces/cli/container.py

@dataclass(frozen=True)
class Container:
    return_repository: ReturnRepository
    result_store: SimulationResultStore
    rng: RNG
    clock: Clock
    renderer: Renderer
    correlation_id: UUID

def build_production_container(profile: SimulationProfile, portfolio_id: UUID) -> Container:
    return Container(
        return_repository=CsvReturnRepository(),
        result_store=JsonlEventWriter(output_dir=Path("./output")),
        rng=NumpyGenerator(seed=profile.seed or SeedSequence().generate_state(1)[0]),
        clock=SystemClock(),
        renderer=MatplotlibRenderer(),
        correlation_id=uuid4(),
    )

def build_test_container(profile: SimulationProfile, portfolio_id: UUID, *, frozen_at: datetime) -> Container:
    return Container(
        return_repository=InMemoryReturnRepository(),
        result_store=InMemoryEventStore(),
        rng=SeededGenerator(seed=42),
        clock=FakeClock(frozen_at=frozen_at),
        renderer=NullRenderer(),
        correlation_id=uuid4(),
    )
```

Use cases consume the `Container`:

```python
# src/application/simulation/run.py

@dataclass(frozen=True)
class RunMonteCarloSimulation:
    container: Container

    def execute(self, profile: SimulationProfile, portfolio: Portfolio) -> RunResult:
        ...
        distribution = self.container.return_repository.load(
            portfolio_id=portfolio.id,
            source=profile.returns_source,
        )
        ...
```

Tests construct their own `Container` via `build_test_container`:

```python
# tests/unit/application/test_run_monte_carlo_simulation.py

def test_run_completes_with_seeded_rng():
    profile = SimulationProfileFactory.build(seed=42)
    portfolio = PortfolioFactory.build()
    container = build_test_container(profile, portfolio.id, frozen_at=datetime(2026, 6, 22))

    result = RunMonteCarloSimulation(container).execute(profile, portfolio)

    assert result.status == COMPLETED
    assert result.metrics.mean_terminal == pytest.approx(...)
```

## Rationale (concrete)

| Property | Hand-rolled | DI library |
|---|---|---|
| Lines of wiring code | ~50 | ~600 (library) + ~50 (config) |
| New runtime dependency | 0 | 1 |
| Failure mode on misconfiguration | Immediate `AttributeError` at startup | Deferred `ContainerError` at first resolve |
| Time to learn the API | 0 (it's just Python) | 1-2 hours (decorators + scopes) |
| `mypy --strict` support | Native | Plugin required for some libs |
| Test setup | One dataclass construction | Container override per test |

The hand-rolled approach is strictly better at this scale. If the system
ever grows past 20 use cases or 20 ports, revisit.

## Future trigger for library adoption

If and only if **all three** become true, adopt `dependency-injector`:

1. > 20 use cases, OR
2. > 20 ports, OR
3. Multiple composition roots (e.g., a CLI + a future HTTP server + a
   future Jupyter kernel).

Until then, the `Container` dataclass is sufficient.

## Consequences

**Positive**
- Zero new dependencies.
- Wiring is plain Python; `mypy --strict` validates it for free.
- Tests are explicit — each test constructs its own `Container`,
  making the test fixtures self-documenting.

**Negative**
- Adding a new Port requires editing `Container`, `build_production_*`,
  `build_test_*`. ~3 small edits. Acceptable.
- No scope management (`@singleton` etc.). Not needed in a single-process
  CLI.

**Reversibility**
- Fully reversible by introducing `dependency-injector` later. The
  use cases already consume a `Container`-shaped object; the migration
  is mechanical.