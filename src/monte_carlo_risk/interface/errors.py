from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any

from monte_carlo_risk.domain.shared_kernel import RunId

_ALLOWED_ERROR_CODES: frozenset[str] = frozenset({"cli_argument_error"})

_EXIT_CODE_BY_ERROR_CODE: dict[str, int] = {"cli_argument_error": 2}

_DEFAULT_EXIT_CODE: int = 2


@dataclass(frozen=True)
class CanonicalCliError:
    error_code: str
    message: str
    run_id: RunId
    context: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.error_code not in _ALLOWED_ERROR_CODES:
            raise ValueError(
                f"error_code {self.error_code!r} is not in the contract enum "
                f"(allowed: {sorted(_ALLOWED_ERROR_CODES)}); update "
                f"cli-contract.yaml §error_schema.error_code and "
                f"_ALLOWED_ERROR_CODES in interface/errors.py together"
            )


def emit_canonical_error(error: CanonicalCliError) -> None:
    payload: dict[str, Any] = {
        "error_code": error.error_code,
        "message": error.message,
        "run_id": str(error.run_id),
    }
    if error.context is not None:
        payload["context"] = error.context
    print(json.dumps(payload, sort_keys=True), file=sys.stderr)
    sys.exit(_EXIT_CODE_BY_ERROR_CODE.get(error.error_code, _DEFAULT_EXIT_CODE))
