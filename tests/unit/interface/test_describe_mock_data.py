from __future__ import annotations

import json

from click.testing import CliRunner

from monte_carlo_risk.interface.cli.app import app
from monte_carlo_risk.interface.cli.commands.describe_mock_data import (
    MOCK_DATA_DESCRIPTOR_STUB,
)

_EXPECTED_STUB: dict[str, object] = {
    "provider": "mock",
    "version": "0.1.0-stub",
    "tickers": [],
    "date_range": {"start": None, "end": None},
    "frequency": "daily",
}


def test_describe_mock_data_returns_stub_matching_contract() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["describe-mock-data"])

    assert result.exit_code == 0, f"expected exit 0, got {result.exit_code}: {result.stderr!r}"
    assert MOCK_DATA_DESCRIPTOR_STUB == _EXPECTED_STUB

    stdout_lines = result.stdout.splitlines()
    assert len(stdout_lines) == 1, (
        f"expected exactly 1 stdout line, got {len(stdout_lines)}: {stdout_lines!r}"
    )

    parsed = json.loads(stdout_lines[0])
    assert parsed == _EXPECTED_STUB


def test_describe_mock_data_stub_has_required_keys() -> None:
    required_keys = {"provider", "version", "tickers", "date_range", "frequency"}
    assert set(MOCK_DATA_DESCRIPTOR_STUB.keys()) == required_keys
    assert MOCK_DATA_DESCRIPTOR_STUB["provider"] == "mock"
    assert MOCK_DATA_DESCRIPTOR_STUB["version"] == "0.1.0-stub"
    assert MOCK_DATA_DESCRIPTOR_STUB["tickers"] == []
    assert MOCK_DATA_DESCRIPTOR_STUB["frequency"] == "daily"
    date_range = MOCK_DATA_DESCRIPTOR_STUB["date_range"]
    assert isinstance(date_range, dict)
    assert set(date_range.keys()) == {"start", "end"}
    assert date_range["start"] is None
    assert date_range["end"] is None


def test_describe_mock_data_emits_exactly_one_stdout_line() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["describe-mock-data"])

    assert result.exit_code == 0
    assert len(result.stdout.splitlines()) == 1
    assert result.stderr == ""


def test_describe_mock_data_emits_no_stderr_on_success() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["describe-mock-data"])

    assert result.exit_code == 0
    assert result.stderr == ""
