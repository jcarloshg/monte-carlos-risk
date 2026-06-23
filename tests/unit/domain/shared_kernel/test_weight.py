"""Unit tests for :class:`monte_carlo_risk.domain.shared_kernel.Weight`."""

from __future__ import annotations

import pytest

from monte_carlo_risk.domain.shared_kernel import InvalidWeightError, Weight


class TestWeightHappyPath:
    """BDD Scenario 1 (Happy Path) — fail-fast, even at the boundaries."""

    @pytest.mark.parametrize("value", [0.0, 0.5, 1.0])
    def test_accepts_unit_interval(self, value: float) -> None:
        assert Weight(value).value == value


class TestWeightEdgeCaseMandatory:
    """BDD Edge Case (MANDATORY) — every invalid input raises at the constructor."""

    @pytest.mark.parametrize(
        "bad_value",
        [-0.1, 1.1, float("nan"), float("inf"), float("-inf")],
    )
    def test_rejects_out_of_range_nan_and_inf_at_construction(self, bad_value: float) -> None:
        with pytest.raises(InvalidWeightError):
            Weight(bad_value)

    @pytest.mark.parametrize(
        ("bad_value", "expected_substring"),
        [
            (float("nan"), "NaN"),
            (float("inf"), "inf"),
            (float("-inf"), "-inf"),
            (1.5, "[0, 1]"),
        ],
    )
    def test_error_messages_are_distinct(self, bad_value: float, expected_substring: str) -> None:
        with pytest.raises(InvalidWeightError) as exc:
            Weight(bad_value)
        assert expected_substring in str(exc.value)
