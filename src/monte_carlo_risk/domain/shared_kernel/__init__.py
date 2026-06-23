"""Shared kernel — cross-context value objects.

These four value objects are the foundation every bounded context
(Portfolio, Simulation, RiskMetrics) inherits. They enforce invariants at
construction time (fail-fast) and live behind a single import surface so
downstream code never reaches into a submodule.
"""

from __future__ import annotations

from monte_carlo_risk.domain.shared_kernel.currency import Currency, InvalidCurrencyError
from monte_carlo_risk.domain.shared_kernel.run_id import InvalidRunIdError, RunId
from monte_carlo_risk.domain.shared_kernel.ticker import InvalidTickerError, Ticker
from monte_carlo_risk.domain.shared_kernel.weight import InvalidWeightError, Weight

__all__ = [
    "Currency",
    "InvalidCurrencyError",
    "InvalidRunIdError",
    "InvalidTickerError",
    "InvalidWeightError",
    "RunId",
    "Ticker",
    "Weight",
]
