from __future__ import annotations

import io
import json
import sys
import uuid

import pytest
from click.testing import CliRunner

from monte_carlo_risk.domain.shared_kernel import RunId
from monte_carlo_risk.interface.cli.app import app
from monte_carlo_risk.interface.errors import CanonicalCliError, emit_canonical_error


def test_emit_canonical_error_writes_one_json_line_to_stderr() -> None:
    rid = RunId()
    error = CanonicalCliError(
        error_code="cli_argument_error",
        message="unknown flag: --bogus",
        context={"flag": "--bogus"},
        run_id=rid,
    )

    captured = io.StringIO()
    original_stderr = sys.stderr
    sys.stderr = captured
    try:
        with pytest.raises(SystemExit) as excinfo:
            emit_canonical_error(error)
    finally:
        sys.stderr = original_stderr

    assert excinfo.value.code == 2
    lines = captured.getvalue().splitlines()
    assert len(lines) == 1, f"expected exactly 1 stderr line, got {len(lines)}: {lines!r}"
    parsed = json.loads(lines[0])
    assert set(parsed.keys()) == {"error_code", "message", "context", "run_id"}
    assert parsed["error_code"] == "cli_argument_error"
    assert parsed["message"] == "unknown flag: --bogus"
    assert parsed["context"] == {"flag": "--bogus"}
    assert parsed["run_id"] == str(rid)


def test_emit_canonical_error_emits_exactly_one_line_per_call() -> None:
    captured = io.StringIO()
    original_stderr = sys.stderr
    sys.stderr = captured
    try:
        with pytest.raises(SystemExit):
            emit_canonical_error(
                CanonicalCliError(
                    error_code="cli_argument_error",
                    message="first",
                    run_id=RunId(),
                )
            )
        with pytest.raises(SystemExit):
            emit_canonical_error(
                CanonicalCliError(
                    error_code="cli_argument_error",
                    message="second",
                    run_id=RunId(),
                )
            )
    finally:
        sys.stderr = original_stderr

    lines = captured.getvalue().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["message"] == "first"
    assert json.loads(lines[1])["message"] == "second"


def test_emit_canonical_error_rejects_unknown_error_code() -> None:
    with pytest.raises(ValueError) as excinfo:
        CanonicalCliError(error_code="not_a_real_code", message="x", run_id=RunId())
    assert "not_a_real_code" in str(excinfo.value)
    assert "cli-contract.yaml" in str(excinfo.value)


def test_unknown_flag_emits_canonical_error_with_exit_code_2() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["describe-mock-data", "--bogus"])

    assert result.exit_code == 2, f"expected exit 2, got {result.exit_code}: {result.stdout!r}"

    stderr_lines = result.stderr.splitlines()
    assert len(stderr_lines) == 1, (
        f"expected exactly 1 stderr line, got {len(stderr_lines)}: {stderr_lines!r}"
    )

    parsed = json.loads(stderr_lines[0])
    assert parsed["error_code"] == "cli_argument_error"
    assert "No such option" in parsed["message"] or "--bogus" in parsed["message"]
    assert "run_id" in parsed
    uuid.UUID(parsed["run_id"])
    assert parsed["run_id"].count("-") == 4


def test_canonical_error_omits_context_when_none() -> None:
    captured = io.StringIO()
    original_stderr = sys.stderr
    sys.stderr = captured
    try:
        with pytest.raises(SystemExit):
            emit_canonical_error(
                CanonicalCliError(
                    error_code="cli_argument_error",
                    message="no context",
                    run_id=RunId(),
                )
            )
    finally:
        sys.stderr = original_stderr

    parsed = json.loads(captured.getvalue().splitlines()[0])
    assert "context" not in parsed
    assert set(parsed.keys()) == {"error_code", "message", "run_id"}
