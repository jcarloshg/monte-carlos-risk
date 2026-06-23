# Architecture — Hexagonal (Ports & Adapters) Map

> Frozen on: 2026-06-23
> Source: Planning ADR-001 (rule), Design ADR-007 (concrete shape).
> Consuming phase: 300 (Coding).
> Related: `c4-container.md`, `data-flow.md`.

This document is the **developer-ready** view of the hexagonal architecture for `monte-carlo-risk`. It complements the rule-level ADR-001 (which says *what* the forbidden-import graph is) by specifying the *concrete* directory tree, port Protocols, and linter contract that the 300 (Coding) phase will implement.

---

## Concrete Layout

```
src/monte_carlo_risk/
  __init__.py                         # __version__, package marker

  domain/                             # PURE. No I/O. numpy + stdlib only.
    __init__.py
    shared_kernel/
      __init__.py
      ticker.py                       # Ticker value object
      weight.py                       # Weight value object
      return_.py                      # Return scalar value object (daily log return)
      currency.py                     # Currency value object
      run_id.py                       # RunId value object (uuid4 wrapper)
    portfolio/
      __init__.py
      holding.py                      # Holding value object (ticker + weight)
      portfolio.py                    # Portfolio aggregate (root)
      invariants.py                   # weights-sum-to-one, no-duplicates
      events.py                       # PortfolioDefined event
    simulation/
      __init__.py
      path.py                         # Path value object (numpy array wrapper)
      path_set.py                     # PathSet aggregate child
      simulation_run.py               # SimulationRun aggregate (root) + state machine
      parameters.py                   # n_paths, horizon, seed, provider
      events.py                       # SimulationStarted, SimulationCompleted
    risk_metrics/
      __init__.py
      var.py                          # VaR computation
      cvar.py                         # CVaR computation
      drawdown.py                     # max drawdown distribution
      risk_report.py                  # RiskReport aggregate (root)
      events.py                       # RiskMetricsCalculated
    visualization/
      __init__.py
      chart_kind.py                   # Enum: paths, drawdown, fan_chart
      chart_artifact.py               # ChartArtifact aggregate (root) — CONTRACT ONLY
      events.py                       # ChartsRendered

  application/                        # USE CASES + PORTS
    __init__.py
    use_cases/
      __init__.py
      run_simulation.py               # the orchestrator (Portfolio → Sim → Risk → Viz)
      validate_portfolio.py           # static-only Portfolio validation
      describe_mock_data.py           # returns MockDataDescriptor
    ports/
      __init__.py
      market_data_source.py           # Protocol: MarketDataSource.load(universe) -> ReturnMatrix
      chart_renderer.py               # Protocol: ChartRenderer.render(artifact, output_path) -> None
      rng.py                          # Protocol: DeterministicRNG.uniform(...), .normal(...), .integers(...)
      return_matrix_loader.py         # Protocol: ReturnMatrixLoader.load(path) -> ReturnMatrix (filesystem adapter)
      output_writer.py                # Protocol: OutputWriter.write_bytes / write_json (filesystem adapter)

  infrastructure/                     # ADAPTERS — implement the Ports
    __init__.py
    market_data/
      __init__.py
      mock_market_data_source.py      # implements MarketDataSource; reads bundled CSV via ReturnMatrixLoader
      http_market_data_source.py      # v2 stub: raises NotImplementedError
    rng/
      __init__.py
      numpy_rng.py                    # implements DeterministicRNG; wraps numpy.random.Generator
    rendering/
      __init__.py
      matplotlib_renderer.py          # implements ChartRenderer
    filesystem/
      __init__.py
      csv_return_matrix_loader.py     # implements ReturnMatrixLoader
      filesystem_output_writer.py     # implements OutputWriter

  interface/                          # CLI ENTRYPOINTS
    __init__.py
    cli/
      __init__.py
      app.py                          # Typer root, composition root (wires adapters)
      commands/
        __init__.py
        simulate.py
        validate_portfolio.py
        describe_mock_data.py
    errors.py                         # canonical JSON error envelope (matches contracts/cli-contract.yaml error_schema)
    logging.py                        # structlog setup; one JSON line per domain event
    cli_contract.py                   # argparse/Typer validators matching cli-contract.yaml

tests/                                # Mirror of src/, plus contract/, plus e2e/
  unit/
    domain/{portfolio,simulation,risk_metrics,visualization}/...
    application/use_cases/...
  contract/
    test_market_data_source_contract.py
    test_rng_contract.py
    test_chart_renderer_contract.py
  integration/
    infrastructure/{market_data,rng,rendering,filesystem}/...
  e2e/
    test_cli_smoke.py
    test_docker_image.py
```

### Why these specific module names

- `domain/shared_kernel/` — value objects shared by multiple bounded contexts (`Ticker`, `Weight`, `Return`, `Currency`, `RunId`). Lifted into a sub-package so the import-linter can whitelist `domain/shared_kernel/` separately if needed.
- `domain/<context>/events.py` — each context owns its own past-tense event classes; events are **value objects** (immutable dataclasses), not callables.
- `application/ports/` — every Protocol lives here. Adapters in `infrastructure/` implement them; domain code never imports them.
- `infrastructure/<capability>/` — adapters grouped by what they adapt, not by bounded context. This makes "add a new chart library" mean "add `infrastructure/rendering/seaborn_renderer.py`", not "modify every context."
- `interface/cli/` — the Typer root + per-command modules. The composition root (`app.py`) is the only place that knows about concrete adapters.

---

## Ports (Protocols)

### `application/ports/market_data_source.py`

```python
from typing import Protocol
from monte_carlo_risk.domain.shared_kernel.ticker import Ticker
from monte_carlo_risk.application.ports.return_matrix_loader import ReturnMatrixLoader  # re-export or separate

class ReturnMatrix: ...  # defined in domain/shared_kernel/ or domain/simulation/

class MarketDataSource(Protocol):
    """Loads a ReturnMatrix for the requested universe of tickers."""

    def load(self, universe: tuple[Ticker, ...]) -> ReturnMatrix:
        """Return a ReturnMatrix covering all tickers in `universe` at the supported frequency.

        Raises:
            MarketDataLoadError: if any ticker cannot be resolved.
            MarketDataCorpusMissingError: if the underlying data source has no data at all.
        """
        ...
```

### `application/ports/rng.py`

```python
from typing import Protocol
import numpy as np

class DeterministicRNG(Protocol):
    """Wraps numpy.random.Generator with a fixed seed for reproducibility (NFR-4)."""

    @property
    def seed(self) -> int: ...

    def uniform(self, low: float = 0.0, high: float = 1.0, size: int | tuple[int, ...] = 1) -> np.ndarray: ...

    def normal(self, loc: float = 0.0, scale: float = 1.0, size: int | tuple[int, ...] = 1) -> np.ndarray: ...

    def integers(self, low: int, high: int | None = None, size: int | tuple[int, ...] = 1) -> np.ndarray: ...

    def spawn(self, child_seed: int) -> "DeterministicRNG":
        """Return a child RNG for sub-simulations (e.g., per-path antithetic streams)."""
        ...
```

### `application/ports/chart_renderer.py`

```python
from typing import Protocol
from pathlib import Path
from monte_carlo_risk.domain.visualization.chart_artifact import ChartArtifact

class ChartRenderer(Protocol):
    """Renders a ChartArtifact (contract owned by domain) to a file."""

    def render(self, artifact: ChartArtifact, output_path: Path) -> None:
        """Write a PNG file at output_path. Raises VisualizationFailed on failure."""
        ...
```

### `application/ports/output_writer.py`

```python
from typing import Protocol
from pathlib import Path

class OutputWriter(Protocol):
    def write_bytes(self, path: Path, data: bytes) -> None: ...
    def write_json(self, path: Path, obj: dict) -> None: ...
    def ensure_directory(self, path: Path) -> None: ...
```

### `application/ports/return_matrix_loader.py`

```python
from typing import Protocol
from pathlib import Path
from monte_carlo_risk.domain.shared_kernel.ticker import Ticker

class ReturnMatrixLoader(Protocol):
    """Loads a single ticker's return series from a filesystem path.

    Used by MockMarketDataSource to read bundled CSV files.
    """

    def load(self, ticker: Ticker, path: Path) -> "ReturnSeries":
        """Return a single-ticker return series. Raises ReturnMatrixLoadError on parse failure."""
        ...
```

---

## Adapters (implementations of the Ports)

| Port | v1 Adapter | v2 Adapter |
|---|---|---|
| `MarketDataSource` | `infrastructure/market_data/mock_market_data_source.py` (reads `data/mock/*.csv` via `ReturnMatrixLoader`) | `infrastructure/market_data/http_market_data_source.py` (stub; raises `NotImplementedError`) |
| `DeterministicRNG` | `infrastructure/rng/numpy_rng.py` (wraps `numpy.random.Generator` from `default_rng(seed)`) | n/a |
| `ChartRenderer` | `infrastructure/rendering/matplotlib_renderer.py` | n/a |
| `OutputWriter` | `infrastructure/filesystem/filesystem_output_writer.py` | n/a |
| `ReturnMatrixLoader` | `infrastructure/filesystem/csv_return_matrix_loader.py` | n/a |

The composition root (`interface/cli/app.py`) wires these at startup:

```python
# Pseudocode only — actual implementation in 300 phase.
rng = NumpyRNG(seed=args.seed)
loader = CsvReturnMatrixLoader(corpus_dir=Path("data/mock"))
data_source = MockMarketDataSource(loader=loader)
renderer = MatplotlibRenderer()
writer = FilesystemOutputWriter()
orchestrator = RunSimulation(
    rng=rng,
    data_source=data_source,
    renderer=renderer,
    output_writer=writer,
)
```

Tests construct the orchestrator with **fake** adapters directly — no DI container needed at this scale.

---

## Linter Contract (`.importlinter`)

Drop this file at the repo root (`/Users/jcarloshg/Documents/school/monte-carlo-risk/.importlinter`):

```ini
[importlinter:contract:domain-purity]
name = Domain purity
type = forbidden
source_modules =
    monte_carlo_risk.domain
forbidden_modules =
    matplotlib
    mpl_toolkits
    pandas
    requests
    httpx
    urllib3
    aiohttp
    typer
    click
    pathlib
    monte_carlo_risk.application
    monte_carlo_risk.infrastructure
    monte_carlo_risk.interface

[importlinter:contract:application-boundary]
name = Application layer does not import infrastructure or interface
type = forbidden
source_modules =
    monte_carlo_risk.application
forbidden_modules =
    monte_carlo_risk.infrastructure
    monte_carlo_risk.interface

[importlinter:contract:no-orm-leak]
name = No ORM/database library anywhere in the codebase
type = forbidden
source_modules =
    monte_carlo_risk
forbidden_modules =
    sqlalchemy
    django
    flask_sqlalchemy
    peewee
    tortoise
    piccolo
    prisma
```

**CI job (`hexagonal-purity`)** runs:

```bash
pip install import-linter
lint-imports
```

A violation fails the build. The contract covers everything forbidden by ADR-001 plus the "no ORM" rule from ADR-009.

---

## Notes

- **No DI container.** Constructor injection through the composition root is sufficient at this scale. If a second use case appears, evaluate `dependency-injector` or a hand-rolled container then — not now.
- **`numpy` is permitted inside `domain/`** per ADR-002. The `domain-purity` contract does NOT list `numpy` in `forbidden_modules`. The linter is intentionally permissive about the math primitive.
- **`pathlib` is forbidden in domain** because it is filesystem I/O; the design uses `OutputWriter` Protocol to abstract this.
- **`mypy --strict`** is run as a separate CI job to catch Protocol drift (e.g., an adapter whose signature doesn't match the Protocol).
