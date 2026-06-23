#!/usr/bin/env bash
# ci_smoke_bootstrap.sh
#
# Happy Path acceptance drill for task-001.
# Simulates "clean clone" by creating a fresh venv and running the bootstrap
# recipe end-to-end. Exits non-zero if anything fails or the budget is exceeded.
#
# Usage:
#   bash scripts/ci_smoke_bootstrap.sh [PYTHON_BIN]
#
# Defaults PYTHON_BIN to python3.12 (CI uses actions/setup-python).

set -eu

PYTHON_BIN="${1:-python3.12}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv-smoke"
START_TS="$(date +%s)"
BUDGET_SECONDS="${BUDGET_SECONDS:-120}"

cd "${REPO_ROOT}"

cleanup() {
    rm -rf "${VENV_DIR}"
}
trap cleanup EXIT

echo "[ci_smoke_bootstrap] creating fresh venv with ${PYTHON_BIN}"
"${PYTHON_BIN}" -m venv "${VENV_DIR}"

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

python -m pip install -U pip >/dev/null
pip install -e ".[dev]" >/dev/null

echo "[ci_smoke_bootstrap] running pytest"
pytest -q

echo "[ci_smoke_bootstrap] running ruff"
ruff check src tests
ruff format --check src tests

echo "[ci_smoke_bootstrap] running mypy"
mypy src

END_TS="$(date +%s)"
ELAPSED=$((END_TS - START_TS))

if [ "${ELAPSED}" -gt "${BUDGET_SECONDS}" ]; then
    echo "[ci_smoke_bootstrap] FAIL: ${ELAPSED}s exceeded budget of ${BUDGET_SECONDS}s" >&2
    exit 1
fi

echo "[ci_smoke_bootstrap] OK in ${ELAPSED}s (budget ${BUDGET_SECONDS}s)"
exit 0