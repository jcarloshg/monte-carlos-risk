from __future__ import annotations

import io
import json
import re
from datetime import datetime

import pytest
import structlog

from monte_carlo_risk.interface.logging import configure_logging

_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")


@pytest.fixture(autouse=True)
def _reset_structlog() -> None:
    structlog.reset_defaults()
    yield
    structlog.reset_defaults()


def test_structlog_json_renderer_emits_one_valid_json_per_line_in_non_tty() -> None:
    buf = io.StringIO()
    configure_logging(log_format="json", stream=buf)
    log = structlog.get_logger()

    log.info("evt1", k=1)
    log.warning("evt2", k=2)
    log.error("evt3", k=3)

    raw = buf.getvalue()
    lines = raw.splitlines()
    assert len(lines) == 3, f"expected 3 lines, got {len(lines)}: {lines!r}"

    for line in lines:
        assert "\n" not in line, f"line contains literal newline: {line!r}"
        parsed = json.loads(line)
        assert isinstance(parsed, dict)
        assert "event" in parsed
        assert "level" in parsed

    parsed_events = [json.loads(ln) for ln in lines]
    assert [p["event"] for p in parsed_events] == ["evt1", "evt2", "evt3"]
    assert [p["level"] for p in parsed_events] == ["info", "warning", "error"]


def test_structlog_text_renderer_in_non_tty_disables_colors() -> None:
    buf = io.StringIO()
    configure_logging(log_format="text", stream=buf)
    log = structlog.get_logger()
    log.info("evt", k=1)

    raw = buf.getvalue()
    assert _ANSI_ESCAPE_RE.search(raw) is None, (
        f"non-TTY text output must not contain ANSI escapes: {raw!r}"
    )


def test_structlog_json_format_includes_iso_timestamp_and_log_level() -> None:
    buf = io.StringIO()
    configure_logging(log_format="json", stream=buf)
    log = structlog.get_logger()
    log.info("evt", k=1)

    line = buf.getvalue().splitlines()[0]
    parsed = json.loads(line)

    assert "timestamp" in parsed
    assert "level" in parsed
    assert "event" in parsed

    datetime.fromisoformat(parsed["timestamp"].replace("Z", "+00:00"))
    assert parsed["level"] == "info"


def test_configure_logging_rejects_invalid_log_format() -> None:
    with pytest.raises(ValueError) as excinfo:
        configure_logging(log_format="xml")
    assert "log_format" in str(excinfo.value)


def test_configure_logging_rejects_invalid_log_level() -> None:
    with pytest.raises(ValueError) as excinfo:
        configure_logging(log_level="TRACE")
    assert "log_level" in str(excinfo.value)
