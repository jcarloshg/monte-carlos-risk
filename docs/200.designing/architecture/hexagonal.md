# Hexagonal Architecture — Ports & Adapters Map

> Source of truth: ADR-002 (hexagonal layout), ADR-006 (seeded RNG),
> ADR-015 (≥ 2 adapters per port), and the frozen folder layout in
> `docs/100.planning/diagrams/c4-container.md` (L2).
>
> This document is the **design-time inventory** the Coding phase will
> implement against. It freezes:
> 1. The 5 Ports (Protocol interfaces in `src/application/ports/`).
> 2. The 2-adapter rule for every Port.
> 3. The wiring point (composition root at `src/interfaces/cli/main.py`).
> 4. The responsibilities of each adapter, no more, no less.

---

## 1. Layer rules (re-stated from ADR-002 + ADR-010)

```
domain         ← pure. imports: numpy, pydantic, decimal, src.domain.**
application    ← pure. imports: src.domain.**, src.application.ports.**
infrastructure ← I/O happens here. imports: src.application.ports.**, src.domain.**
interfaces     ← composition root + CLI. imports: src.application.**, src.infrastructure.**
shared_kernel  ← independent. imports: numpy, pydantic, decimal.
```

The import-linter contract in `.importlinter` enforces these. `mypy --strict`
validates Protocol conformance.

---

## 2. Port inventory (frozen, 5 ports)

Each Port is a `typing.Protocol` (or `@runtime_checkable` Protocol where
needed). The Protocol is the only thing the application/domain layers
import; the concrete adapter is invisible to them.

### 2.1 `ReturnRepository`

**Location:** `src/application/ports/return_repository.py`

```python
class ReturnRepository(Protocol):
    def load(self, *, portfolio_id: UUID, source: ReturnsSource) -> ReturnDistribution:
        ...
```

| Adapter | Location | Responsibility |
|---|---|---|
| `CsvReturnRepository` (prod) | `src/infrastructure/csv/csv_return_repository.py` | Reads `data/mock/<portfolioId>.csv`, parses with stdlib `csv`, returns a `ReturnDistribution`. |
| `InMemoryReturnRepository` (test) | `tests/adapters/in_memory_return_repository.py` | Holds a `dict[UUID, ReturnDistribution]` populated by test fixtures. |

**Rationale:** the future `MarketDataAcl` (per ADR-001) replaces the CSV
adapter; the Protocol stays.

### 2.2 `SimulationResultStore`

**Location:** `src/application/ports/simulation_result_store.py`

```python
class SimulationResultStore(Protocol):
    def open_run(self, run_id: UUID, profile: SimulationProfile, portfolio_id: UUID) -> None: ...
    def write_event(self, envelope: EventEnvelope) -> None: ...
    def flush(self) -> None: ...
    def write_status(self, status: SimulationStatus) -> None: ...
    def write_metrics(self, run_id: UUID, metrics: RiskMetrics) -> None: ...
    def read_events(self, run_id: UUID) -> list[EventEnvelope]: ...   # for replay
    def read_status(self, run_id: UUID) -> SimulationStatus: ...
```

| Adapter | Location | Responsibility |
|---|---|---|
| `JsonlEventWriter` (prod) | `src/infrastructure/persistence/jsonl_event_writer.py` | Writes JSONL with per-batch flush (ADR-009). Reads back via `pathlib` + `json`. |
| `InMemoryEventStore` (test) | `tests/adapters/in_memory_event_store.py` | Holds a `dict[UUID, list[EventEnvelope]]` + `dict[UUID, SimulationStatus]`. |

**Rationale:** ADR-003 freezes the JSONL format. ADR-014 documents why no
transactional outbox is needed.

### 2.3 `RNG`

**Location:** `src/application/ports/rng.py`

```python
class RNG(Protocol):
    def normal(self, loc: float, scale: float, size: tuple[int, ...]) -> np.ndarray: ...
    def integers(self, low: int, high: int, size: tuple[int, ...]) -> np.ndarray: ...
    def choice(self, a: np.ndarray, size: tuple[int, ...], replace: bool) -> np.ndarray: ...
```

| Adapter | Location | Responsibility |
|---|---|---|
| `NumpyGenerator` (prod) | `src/infrastructure/random/numpy_generator.py` | Wraps `numpy.random.Generator` constructed from `numpy.random.SeedSequence(seed)`. |
| `SeededGenerator` (test) | `tests/adapters/seeded_generator.py` | A pre-seeded `Generator(42)` instance with a frozen state for unit tests. |

**Rationale:** ADR-006 freezes the Protocol shape + the persistence of the
seed on every run.

### 2.4 `Clock`

**Location:** `src/application/ports/clock.py`

```python
class Clock(Protocol):
    def now_utc(self) -> datetime: ...
    def monotonic(self) -> float: ...   # for wall-clock self-timeout (ADR-007 + 300-Q6.6)
```

| Adapter | Location | Responsibility |
|---|---|---|
| `SystemClock` (prod) | `src/domain/shared_kernel/clock.py` (shared_kernel because the domain uses it for `occurredAt`) | `datetime.now(tz=UTC)`, `time.monotonic()`. |
| `FakeClock` (test) | `tests/adapters/fake_clock.py` | Returns a frozen `datetime` injected at construction; tests advance it manually. |

**Rationale:** the domain needs `Clock` to produce reproducible
`occurredAt` timestamps, so it lives in `shared_kernel/` per ADR-007.
The Protocol is in `ports/`; the production impl is in `shared_kernel/`.

### 2.5 `Renderer`

**Location:** `src/application/ports/renderer.py`

```python
class Renderer(Protocol):
    def render_fan_chart(self, paths: np.ndarray, output_path: Path) -> None: ...
    def render_drawdown_hist(self, drawdowns: np.ndarray, output_path: Path) -> None: ...
    def render_terminal_wealth_hist(self, terminal: np.ndarray, output_path: Path) -> None: ...
```

| Adapter | Location | Responsibility |
|---|---|---|
| `MatplotlibRenderer` (prod) | `src/infrastructure/matplotlib/matplotlib_renderer.py` | Uses matplotlib to write PNGs to `./output/<runId>/`. |
| `NullRenderer` (test) | `tests/adapters/null_renderer.py` | Discards the call; asserts on call args in tests. |

**Rationale:** the future `Reporting` context (per ADR-001) replaces the
matplotlib adapter; the Protocol stays.

---

## 3. Composition root wiring (ADR-016)

**Location:** `src/interfaces/cli/main.py`

```python
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

The use cases receive `Container` (or just the ports they need) via
constructor injection. There is no `inject` decorator, no `@singleton`
scope, no XML config. Pythonic dataclasses are sufficient for v1.

---

## 4. Use cases (3 frozen)

| Use case | Location | Ports consumed |
|---|---|---|
| `RunMonteCarloSimulation` | `src/application/simulation/run.py` | `ReturnRepository`, `SimulationResultStore`, `RNG`, `Clock`, `Renderer` |
| `ComparePortfolios` | `src/application/simulation/compare.py` | All 5 (same as above; runs twice) |
| `ReplaySimulation` | `src/application/simulation/replay.py` | `SimulationResultStore` (read), `RNG`, `Clock`, `Renderer` (no `ReturnRepository`; uses the persisted returns reference) |

Each use case is a single Python function (or a `@dataclass` with one
`execute()` method). Use cases do not import any adapter directly; they
type-hint on Ports.

---

## 5. Mapper policy (Defining 300-Q2.6)

Every adapter returns **domain objects**, never raw dicts or DataFrames.

| Adapter | Mapper |
|---|---|
| `CsvReturnRepository.load()` | `csv_row → Return` via `_row_to_return()` in the same file |
| `JsonPortfolioRepository.read()` | `dict → Portfolio` via Pydantic `model_validate()` |
| `JsonlEventWriter.write_event()` | `EventEnvelope → dict` via `envelope.model_dump(mode="json")` |
| `MatplotlibRenderer.render_*()` | `np.ndarray → PNG bytes` (no domain mapping; the array IS the domain object) |

Mappers live next to the adapter that produces them. No "Mapper" sub-
package.

---

## 6. Swappability verification (ADR-015 rule)

For each Port, **two adapters must exist at design time**. The list above
satisfies this:

| Port | Production | In-memory | Status |
|---|---|---|---|
| `ReturnRepository` | `CsvReturnRepository` | `InMemoryReturnRepository` | OK |
| `SimulationResultStore` | `JsonlEventWriter` | `InMemoryEventStore` | OK |
| `RNG` | `NumpyGenerator` | `SeededGenerator` | OK |
| `Clock` | `SystemClock` | `FakeClock` | OK |
| `Renderer` | `MatplotlibRenderer` | `NullRenderer` | OK |

A code-review checklist item: "every new Port has ≥ 2 adapters; if you
added a Port with only one, justify why in the PR description." This rule
is enforced socially (PR review) because mechanical enforcement is
impractical without a custom pytest plugin.

---

## 7. Anti-corruption layer (ACL) policy

When a future vendor replaces `CsvReturnRepository` (per ADR-001), the ACL
lives at the adapter boundary:

```
MarketDataAcl (in src/infrastructure/market_data/)
  ├── vendor_client.py            # raw HTTP client, returns vendor-shaped dicts
  ├── vendor_to_domain_mapper.py  # dict → ReturnDistribution (no domain imports)
  └── market_data_return_repository.py  # implements ReturnRepository; uses vendor_client
```

The ACL maps vendor shapes to domain shapes **before** the domain ever
sees the data. The domain layer never imports anything vendor-specific.

For v1 there are no vendors (Defining Q4.1), so no ACL exists yet. The
folder `src/infrastructure/market_data/` is reserved (currently empty).

---

## 8. Summary table (for the Coding phase)

| Port | Domain methods | Production adapter path | Test adapter path |
|---|---|---|---|
| `ReturnRepository` | `load(...)` | `src/infrastructure/csv/csv_return_repository.py` | `tests/adapters/in_memory_return_repository.py` |
| `SimulationResultStore` | `open_run, write_event, flush, write_status, write_metrics, read_events, read_status` | `src/infrastructure/persistence/jsonl_event_writer.py` | `tests/adapters/in_memory_event_store.py` |
| `RNG` | `normal, integers, choice` | `src/infrastructure/random/numpy_generator.py` | `tests/adapters/seeded_generator.py` |
| `Clock` | `now_utc, monotonic` | `src/domain/shared_kernel/clock.py` | `tests/adapters/fake_clock.py` |
| `Renderer` | `render_fan_chart, render_drawdown_hist, render_terminal_wealth_hist` | `src/infrastructure/matplotlib/matplotlib_renderer.py` | `tests/adapters/null_renderer.py` |

The Coding phase implements these paths verbatim. Any deviation requires a
new ADR superseding this document.