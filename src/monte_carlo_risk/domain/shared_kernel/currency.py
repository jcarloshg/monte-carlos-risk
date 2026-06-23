"""Currency value object (ISO-4217 v1).

Subclass of :class:`str` that enforces three uppercase letters (the minimal
ISO-4217 alpha-3 subset; numeric codes are not supported in this version).
"""

from __future__ import annotations

import re

_ISO4217_V1 = re.compile(r"^[A-Z]{3}$")


class InvalidCurrencyError(ValueError):
    """Raised when a currency code violates the ISO-4217 v1 pattern."""


class Currency(str):
    """A validated three-letter uppercase currency code (e.g. ``"USD"``)."""

    __slots__ = ()

    def __new__(cls, value: str) -> Currency:
        if not _ISO4217_V1.fullmatch(value):
            raise InvalidCurrencyError("currency must be three uppercase letters (ISO-4217)")
        return super().__new__(cls, value)

    @property
    def value(self) -> str:
        """The underlying currency code string."""
        return str(self)

    def __repr__(self) -> str:
        return f"Currency({str(self)!r})"
