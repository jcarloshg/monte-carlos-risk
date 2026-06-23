"""Unit tests for :class:`monte_carlo_risk.domain.shared_kernel.Currency`."""

from __future__ import annotations

import pytest

from monte_carlo_risk.domain.shared_kernel import Currency, InvalidCurrencyError


class TestCurrencyHappyPath:
    """BDD Scenario 1 (Happy Path) — Currency accepts three uppercase letters."""

    @pytest.mark.parametrize("code", ["USD", "EUR", "AAA", "JPY", "GBP"])
    def test_currency_accepts_three_uppercase_letters(self, code: str) -> None:
        currency = Currency(code)
        assert currency.value == code

    def test_currency_str_equality_with_raw_string(self) -> None:
        assert Currency("USD") == "USD"


class TestCurrencySadPath:
    """BDD Sad Path — Currency rejects anything that is not three uppercase letters."""

    @pytest.mark.parametrize(
        "bad_value",
        [
            "usd",  # lowercase
            "US",  # two letters
            "USDD",  # four letters
            "US1",  # digit instead of letter
            "US-",  # punctuation
            "",  # empty
            " USD",  # leading whitespace
            "USD ",  # trailing whitespace
        ],
    )
    def test_rejects_malformed_currency_codes(self, bad_value: str) -> None:
        with pytest.raises(InvalidCurrencyError):
            Currency(bad_value)
