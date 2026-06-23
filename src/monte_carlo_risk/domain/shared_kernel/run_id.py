"""RunId value object — stable UUID4-based run identifier (cli-contract.yaml)."""

from __future__ import annotations

import uuid


class InvalidRunIdError(ValueError):
    """Raised when a value cannot be parsed as a :class:`uuid.UUID`."""


class RunId(uuid.UUID):
    """A UUID4-based run identifier.

    Accepts no args (fresh UUID4), a :class:`uuid.UUID`, or a hex string.
    Overrides ``__init__`` only — :class:`uuid.UUID` is C-implemented and
    ``super().__new__`` does not accept kwargs, so the default ``__new__``
    must remain in place.
    """

    __slots__ = ()

    def __init__(self, value: str | uuid.UUID | None = None) -> None:
        if value is None:
            super().__init__(bytes=uuid.uuid4().bytes)
            return
        if isinstance(value, RunId):
            super().__init__(bytes=value.bytes)
            return
        if isinstance(value, uuid.UUID):
            super().__init__(bytes=value.bytes)
            return
        if isinstance(value, str):
            try:
                super().__init__(hex=value)
            except (ValueError, TypeError) as exc:
                raise InvalidRunIdError(f"invalid run id: {value!r}") from exc
            return
        raise InvalidRunIdError(f"invalid run id: {type(value).__name__}")

    @property
    def value(self) -> uuid.UUID:
        return self

    @classmethod
    def generate(cls) -> RunId:
        return cls(uuid.uuid4())
