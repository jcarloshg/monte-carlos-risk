"""Weight value object.

Subclass of :class:`float` that enforces a value in the closed unit interval
``[0, 1]`` at construction time, rejecting ``NaN`` and ``+/-inf``. Used as the
canonical portfolio allocation weight.
"""

from __future__ import annotations

import math


class InvalidWeightError(ValueError):
    """Raised when a weight is outside ``[0, 1]`` or non-finite."""


class Weight(float):
    """A validated portfolio allocation weight in ``[0, 1]``."""

    __slots__ = ()

    def __new__(cls, value: float) -> Weight:
        if math.isnan(value):
            raise InvalidWeightError("weight must be a finite number, got NaN")
        if math.isinf(value):
            sign = "-" if value < 0 else ""
            raise InvalidWeightError(f"weight must be a finite number, got {sign}inf")
        if not 0 <= value <= 1:
            raise InvalidWeightError("weight must be in [0, 1]")
        return super().__new__(cls, value)

    @property
    def value(self) -> float:
        """The underlying numeric weight."""
        return float(self)

    def __repr__(self) -> str:
        return f"Weight({float(self)!r})"
