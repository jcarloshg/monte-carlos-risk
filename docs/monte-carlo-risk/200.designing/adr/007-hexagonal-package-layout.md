# ADR-007 — Hexagonal Package Layout

- **Status:** Accepted
- **Date:** 2026-06-23
- **Deciders:** jcarloshg
- **Source:** Planning ADR-001 (rule); `02.designing.md` §2 (micro architecture); `architecture/hexagonal.md`.
- **Supplements:** Planning ADR-001 (which states *what* the forbidden-import graph is; this ADR specifies *where* every concept lives in the directory tree).

## Context

Planning ADR-001 established the **rule**: `domain/` must not import `infrastructure/`, `application/`, `interface/`, or any I/O library. The Design phase must translate this rule into a **concrete, developer-implementable package layout** that the 300 (Coding) phase can scaffold from without further architectural decisions.

A separate ADR is warranted (vs. amending ADR-001) because the layout is a code-structure decision distinct from the layering rule. New contributors can read either independently: ADR-001 for "what can't import what," ADR-007 for "where does X live."

## Options

1. **Two-layer split.** `core/` (domain + application) vs `adapters/` (infrastructure + interface). Simpler, but mixes domain with application — violates the Planning rule that `application/` may depend on `domain/` but the reverse is forbidden.
2. **Four-layer split, flat.** `domain.py`, `application.py`, `infrastructure.py`, `interface.py` — single files per layer. Impractical at any non-trivial size.
3. **Four-layer split, by bounded context.** `domain/{portfolio,simulation,risk_metrics,visualization}/`, `application/{use_cases,ports}/`, `infrastructure/{market_data,rng,rendering,filesystem}/`, `interface/cli/{commands}/`. Each layer is split by its natural sub-units.

## Decision

**Option 3: four-layer split, by bounded context in domain and by capability in infrastructure.**

The concrete tree (full version in `architecture/hexagonal.md`):

```
src/monte_carlo_risk/
  domain/
    shared_kernel/           # Ticker, Weight, Return, Currency, RunId
    portfolio/               # Portfolio aggregate + Holding + invariants + PortfolioDefined event
    simulation/              # SimulationRun aggregate + PathSet + state machine + Sim events
    risk_metrics/            # RiskReport aggregate + VaR/CVaR/drawdown + RiskMetricsCalculated
    visualization/           # ChartArtifact aggregate (CONTRACT ONLY, no rendering) + ChartsRendered
  application/
    use_cases/               # RunSimulation, ValidatePortfolio, DescribeMockData
    ports/                   # MarketDataSource, ChartRenderer, DeterministicRNG, OutputWriter, ReturnMatrixLoader (Protocols)
  infrastructure/
    market_data/             # MockMarketDataSource (v1), HttpMarketDataSource (v2 stub)
    rng/                     # NumpyRNG
    rendering/               # MatplotlibRenderer
    filesystem/              # CsvReturnMatrixLoader, FilesystemOutputWriter
  interface/
    cli/                     # Typer root + per-command modules + composition root
    errors.py                # canonical JSON error envelope (cli-contract.yaml error_schema)
    logging.py               # structlog setup
    cli_contract.py          # argparse/Typer validators matching cli-contract.yaml
```

### Naming conventions

- **Files** are snake_case and named after the **primary class** they contain (`portfolio.py` contains `class Portfolio`).
- **Test files** mirror source files (`tests/unit/domain/portfolio/test_portfolio.py`).
- **Protocols** are named after the role (`MarketDataSource`, not `IMarketDataSource` — Python uses duck typing; the `I`-prefix is a Java/C# artifact).
- **Adapter implementations** are named `<Library><Role>` (`MatplotlibRenderer`, `NumpyRNG`, `CsvReturnMatrixLoader`).

### Forbidden-import enforcement

The `.importlinter` config in `architecture/hexagonal.md` §Linter Contract encodes:
- `domain/*` cannot import any of: `matplotlib`, `pandas`, `requests`, `httpx`, `typer`, `click`, `pathlib`, `monte_carlo_risk.application`, `monte_carlo_risk.infrastructure`, `monte_carlo_risk.interface`.
- `application/*` cannot import `infrastructure/*` or `interface/*`.
- No ORM/database library may be imported anywhere (`sqlalchemy`, `django`, `peewee`, `tortoise`, `piccolo`, `prisma`).

`mypy --strict` is run as a separate CI job to catch Protocol drift.

## Consequences

**Positive.**
- A new contributor can scaffold the project from this ADR alone; no tribal knowledge needed.
- Adding a new bounded context (e.g., `Reporting`) means adding exactly one directory under each layer with the conventional name.
- Adding a new infrastructure adapter (e.g., a Seaborn renderer) means adding exactly one file under `infrastructure/rendering/` with the conventional name.
- The `.importlinter` config is the single automated guard; reviewers do not need to remember the rules.

**Negative.**
- Slight overhead for a one-developer, one-process project. Mitigated by the rules generating < 100 ms of CI overhead and the clarity benefit for future contributors.
- Adding a fifth context later requires touching four directories. Mitigated by the convention being consistent enough that this is a mechanical change.

**Supersedes.** None (supplements Planning ADR-001).
