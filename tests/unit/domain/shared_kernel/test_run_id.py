"""Unit tests for :class:`monte_carlo_risk.domain.shared_kernel.RunId`."""

from __future__ import annotations

import uuid

import pytest

from monte_carlo_risk.domain.shared_kernel import InvalidRunIdError, RunId


class TestRunIdHappyPath:
    """BDD Scenario 1 (Happy Path)."""

    @pytest.mark.parametrize(
        "factory",
        [
            lambda: RunId(),
            lambda: RunId(uuid.uuid4()),
            lambda: RunId.generate(),
        ],
    )
    def test_default_construction_produces_uuid4(self, factory) -> None:
        rid = factory()
        assert isinstance(rid.value, uuid.UUID)
        assert rid.version == 4

    def test_accepts_explicit_uuid_string(self) -> None:
        rid = RunId("11111111-2222-3333-4444-555555555555")
        assert str(rid) == "11111111-2222-3333-4444-555555555555"

    def test_accepts_nil_uuid(self) -> None:
        nil = uuid.UUID("00000000-0000-0000-0000-000000000000")
        assert RunId(nil).value == nil

    def test_round_trips_through_string(self) -> None:
        original = uuid.uuid4()
        assert RunId(original) == RunId(str(original))

    def test_re_wrapping_is_noop(self) -> None:
        original = RunId()
        assert RunId(original) == original


class TestRunIdSadPath:
    """BDB Sad Path."""

    @pytest.mark.parametrize(
        "bad_value",
        [
            "not-a-uuid",
            "12345",
            "00000000-0000-0000-0000",
            "ZZZZZZZZ-ZZZZ-ZZZZ-ZZZZ-ZZZZZZZZZZZZ",
        ],
    )
    def test_rejects_malformed_uuid_strings(self, bad_value: str) -> None:
        with pytest.raises(InvalidRunIdError):
            RunId(bad_value)
