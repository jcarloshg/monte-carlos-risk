from __future__ import annotations

from monte_carlo_risk.domain.shared_kernel import RunId

LOG_LEVELS: frozenset[str] = frozenset({"DEBUG", "INFO", "WARNING", "ERROR"})

LOG_FORMATS: frozenset[str] = frozenset({"json", "text"})


class InvalidLogLevelError(ValueError):
    pass


class InvalidLogFormatError(ValueError):
    pass


def validate_log_level(value: str) -> str:
    upper = value.upper()
    if upper not in LOG_LEVELS:
        raise InvalidLogLevelError(
            f"--log-level must be one of {sorted(LOG_LEVELS)}, got {value!r}"
        )
    return upper


def validate_log_format(value: str) -> str:
    lower = value.lower()
    if lower not in LOG_FORMATS:
        raise InvalidLogFormatError(
            f"--log-format must be one of {sorted(LOG_FORMATS)}, got {value!r}"
        )
    return lower


def parse_run_id(value: str) -> RunId:
    if value == "auto":
        return RunId()
    return RunId(value)
