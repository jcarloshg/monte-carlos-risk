"""Unit tests for :class:`monte_carlo_risk.domain.shared_kernel.Ticker`."""

from __future__ import annotations

import pytest

from monte_carlo_risk.domain.shared_kernel import InvalidTickerError, Ticker


class TestTickerHappyPath:
    """BDD Scenario 1 (Happy Path)."""

    @pytest.mark.parametrize(
        "value",
        ["AAPL", "BRK.B", "BRK-B", "A1", "MSFT"],
    )
    def test_accepts_valid_ticker(self, value: str) -> None:
        assert Ticker(value).value == value

    def test_str_equality_with_raw_string(self) -> None:
        assert Ticker("AAPL") == "AAPL"
        assert Ticker("AAPL") != "aapl"

    def test_hashable_as_dict_key(self) -> None:
        assert {Ticker("AAPL"): 1}[Ticker("AAPL")] == 1


class TestTickerSadPath:
    """BDD Scenario 2 (Sad Path)."""

    def test_rejects_lowercase_with_exact_message(self) -> None:
        with pytest.raises(InvalidTickerError) as exc:
            Ticker("aapl")
        assert str(exc.value) == "ticker must match ^[A-Z0-9.-]+$"

    @pytest.mark.parametrize(
        "bad_value",
        [
            "",
            "aapl",
            "AAPL ",
            " AAPL",
            "AAéPL",
            "AAPL ",  # NBSP (U+00A0)  # noqa: RUF001
            "AA１L",  # unicode digit  # noqa: RUF001
            "AA PL",
            "AAPL!",
            "AAPL/ETH",
        ],
    )
    def test_rejects_malformed_inputs(self, bad_value: str) -> None:
        with pytest.raises(InvalidTickerError):
            Ticker(bad_value)
