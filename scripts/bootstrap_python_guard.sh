#!/usr/bin/env bash
# bootstrap_python_guard.sh
#
# Reject Python interpreters older than 3.12 so the rest of `make bootstrap`
# never silently installs on the wrong runtime (Sad Path BDD Scenario).
#
# Exit codes:
#   0 — interpreter is >= 3.12, proceed.
#   1 — no interpreter on PATH.
#   2 — interpreter older than 3.12.

set -u

PYTHON_BIN="${PYTHON:-}"

if [ -z "${PYTHON_BIN}" ]; then
    if command -v python3.12 >/dev/null 2>&1; then
        PYTHON_BIN="python3.12"
    elif command -v python3 >/dev/null 2>&1; then
        PYTHON_BIN="python3"
    else
        echo "Python 3.12 required (no python interpreter on PATH)" >&2
        exit 1
    fi
fi

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    echo "Python 3.12 required ('${PYTHON_BIN}' not found)" >&2
    exit 1
fi

if ! "${PYTHON_BIN}" - <<'PY' 2>/dev/null
import sys
sys.exit(0 if sys.version_info >= (3, 12) else 1)
PY
then
    echo "Python 3.12 required (found $(${PYTHON_BIN} -V 2>&1))" >&2
    exit 2
fi

echo "Using interpreter: $(${PYTHON_BIN} -V 2>&1)"
exit 0