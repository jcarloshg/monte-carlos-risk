"""Ticker value object.

Subclass of :class:`str` that enforces a strict uppercase ticker pattern
(``^[A-Z0-9.-]+$``) at construction time. Used as the canonical portfolio item
identifier everywhere a ticker symbol crosses a boundary.
"""

from __future__ import annotations

import re

_TICKER_REGEX = re.compile(r"^[A-Z0-9.-]+$")


class InvalidTickerError(ValueError):
    """Raised when a ticker symbol violates the allowed pattern."""


class Ticker(str):
    """A validated ticker symbol (e.g. ``"AAPL"``, ``"BRK.B"``)."""

    __slots__ = ()

    def __new__(cls, value: str) -> Ticker:
        if not _TICKER_REGEX.fullmatch(value):
            raise InvalidTickerError("ticker must match ^[A-Z0-9.-]+$")
        return super().__new__(cls, value)

    @property
    def value(self) -> str:
        """The underlying ticker string."""
        return str(self)

    def __repr__(self) -> str:
        return f"Ticker({str(self)!r})"
