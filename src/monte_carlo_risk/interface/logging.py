from __future__ import annotations

import logging
import sys
from typing import TextIO

import structlog

DEFAULT_LOGGING: dict[str, str] = {"log_level": "INFO", "log_format": "json"}


def configure_logging(
    *,
    log_level: str = "INFO",
    log_format: str = "json",
    stream: TextIO | None = None,
) -> None:
    if stream is None:
        stream = sys.stderr

    is_tty = bool(getattr(stream, "isatty", lambda: False)())

    if log_format == "json":
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer(sort_keys=True)
    elif log_format == "text":
        renderer = structlog.dev.ConsoleRenderer(colors=is_tty)
    else:
        raise ValueError(f"log_format must be 'json' or 'text', got {log_format!r}")

    level_int = logging.getLevelName(log_level.upper())
    if not isinstance(level_int, int):
        raise ValueError(f"log_level must be DEBUG/INFO/WARNING/ERROR, got {log_level!r}")

    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.dict_tracebacks,
        renderer,
    ]

    structlog.reset_defaults()
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level_int),
        logger_factory=structlog.PrintLoggerFactory(file=stream),
        cache_logger_on_first_use=False,
    )
