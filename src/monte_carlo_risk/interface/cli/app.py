from __future__ import annotations

import sys
from typing import Any

import click
import typer
from typer._click.exceptions import UsageError as TyperUsageError
from typer.main import get_command

from monte_carlo_risk.domain.shared_kernel import InvalidRunIdError, RunId
from monte_carlo_risk.interface.cli.commands.describe_mock_data import describe_mock_data
from monte_carlo_risk.interface.cli_contract import (
    InvalidLogFormatError,
    InvalidLogLevelError,
    parse_run_id,
    validate_log_format,
    validate_log_level,
)
from monte_carlo_risk.interface.errors import CanonicalCliError, emit_canonical_error
from monte_carlo_risk.interface.logging import configure_logging

_current_run_id: RunId = RunId()


def _emit_cli_argument_error(
    *,
    message: str,
    context: dict[str, Any],
    run_id: RunId,
) -> None:
    emit_canonical_error(
        CanonicalCliError(
            error_code="cli_argument_error",
            message=message,
            context=context,
            run_id=run_id,
        )
    )


class _MonteCarloApp(typer.Typer):
    @property
    def name(self) -> str:
        return str(self.info.name)

    def main(
        self,
        args: list[str] | None = None,
        prog_name: str | None = None,
        **extra: Any,
    ) -> Any:
        try:
            cmd = get_command(self)
            return cmd.main(
                args=args,
                prog_name=prog_name or self.info.name,
                standalone_mode=False,
                **extra,
            )
        except (typer.BadParameter, TyperUsageError, click.exceptions.UsageError) as exc:
            _emit_cli_argument_error(
                message=str(exc),
                context={"argv": sys.argv[1:]},
                run_id=_current_run_id,
            )
            raise typer.Exit(2) from None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.main(*args, **kwargs)


app: typer.Typer = _MonteCarloApp(
    name="monte-carlo",
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False,
    pretty_exceptions_show_locals=False,
)


def _set_log_level(value: str) -> str:
    try:
        level = validate_log_level(value)
    except InvalidLogLevelError as exc:
        _emit_cli_argument_error(
            message=str(exc),
            context={"flag": "--log-level", "value": value},
            run_id=_current_run_id,
        )
        raise typer.Exit(2) from None
    configure_logging(log_level=level)
    return value


def _set_log_format(value: str) -> str:
    try:
        fmt = validate_log_format(value)
    except InvalidLogFormatError as exc:
        _emit_cli_argument_error(
            message=str(exc),
            context={"flag": "--log-format", "value": value},
            run_id=_current_run_id,
        )
        raise typer.Exit(2) from None
    configure_logging(log_format=fmt)
    return value


def _set_run_id(value: str) -> str:
    global _current_run_id
    try:
        _current_run_id = parse_run_id(value)
    except (InvalidRunIdError, ValueError) as exc:
        _emit_cli_argument_error(
            message=str(exc),
            context={"flag": "--run-id", "value": value},
            run_id=RunId(),
        )
        raise typer.Exit(2) from None
    return value


@app.callback()
def _root_callback(
    log_level: str = typer.Option("INFO", "--log-level", callback=_set_log_level),
    log_format: str = typer.Option("json", "--log-format", callback=_set_log_format),
    run_id: str = typer.Option("auto", "--run-id", callback=_set_run_id),
) -> None:
    pass


app.command(name="describe-mock-data")(describe_mock_data)
