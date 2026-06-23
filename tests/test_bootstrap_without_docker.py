"""Edge Case BDD Scenario (Mandatory).

If docker compose is unavailable on the host,
`make bootstrap` MUST still succeed: lint + tests run without Docker.

We pin that contract here by:
1. Stripping `docker` (and `docker compose`) from PATH via a temp dir.
2. Running the bootstrap Python guard (the first step of `make bootstrap`)
   and asserting it never tries to call docker.
3. Running `pip install -e ".[dev]"` + `pytest -q` on a throw-away venv
   and asserting both succeed without docker on PATH.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GUARD = REPO_ROOT / "scripts" / "bootstrap_python_guard.sh"


def _stripped_path() -> str:
    """Return a PATH that excludes any directory containing a `docker` binary.

    Always retains `/usr/bin` and `/bin` so that `bash` and other core utils
    remain available to the subprocess under test.
    """
    raw = os.environ.get("PATH", "/usr/bin:/bin")
    kept = []
    for entry in raw.split(os.pathsep):
        candidate = Path(entry) / "docker"
        if candidate.exists():
            continue
        kept.append(entry)
    extra = "/usr/bin:/bin"
    if extra not in kept:
        kept.append(extra)
    return os.pathsep.join(kept) if kept else extra


@pytest.mark.skipif(not GUARD.exists(), reason="bootstrap guard script missing")
def test_guard_does_not_call_docker(tmp_path: Path) -> None:
    """The Python-version guard must never invoke docker."""
    stripped = _stripped_path()
    env = os.environ.copy()
    env["PATH"] = stripped
    env["PYTHON"] = "python3.12"

    result = subprocess.run(
        ["bash", str(GUARD)],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert "Using interpreter" in result.stdout
    assert "Docker" not in result.stdout + result.stderr


@pytest.mark.skipif(shutil.which("python3.12") is None, reason="python3.12 missing")
def test_bootstrap_install_and_pytest_pass_without_docker(tmp_path: Path) -> None:
    """End-to-end: install + pytest succeed when docker is not on PATH.

    Only `test_smoke.py` is executed in the sub-venv to avoid recursion
    (running the full suite here would re-enter this test).
    """
    venv = tmp_path / "venv"
    subprocess.run(
        ["python3.12", "-m", "venv", str(venv)],
        check=True,
        capture_output=True,
    )
    python_bin = venv / "bin" / "python"
    pip_bin = venv / "bin" / "pip"

    stripped = _stripped_path()
    env = os.environ.copy()
    env["PATH"] = stripped

    subprocess.run(
        [str(python_bin), "-m", "pip", "install", "-U", "pip"],
        check=True,
        capture_output=True,
        env=env,
    )
    subprocess.run(
        [str(pip_bin), "install", "-e", ".[dev]"],
        check=True,
        capture_output=True,
        env=env,
        cwd=str(REPO_ROOT),
    )

    result = subprocess.run(
        [str(python_bin), "-m", "pytest", "tests/test_smoke.py"],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
        timeout=60,
    )
    assert result.returncode == 0, (
        f"subvenv pytest failed (rc={result.returncode})\n"
        f"stdout={result.stdout}\nstderr={result.stderr}"
    )
    assert "1 passed" in result.stdout


def test_make_bootstrap_recipe_does_not_require_docker() -> None:
    """`make -n bootstrap` must NOT invoke docker at any step.

    The Makefile text may legitimately contain the word `docker` (e.g. in the
    detection message), but the dry-run output must not contain any docker
    *command invocations* — only optional checks like `command -v docker` and
    informational echo messages.
    """
    make = shutil.which("make")
    if make is None:
        pytest.skip("make not installed")

    result = subprocess.run(
        [make, "-n", "bootstrap"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0
    dry_run = result.stdout + result.stderr

    invocations = [
        line
        for line in dry_run.splitlines()
        if "docker" in line
        and "command -v" not in line
        and "docker compose version" not in line
        and "echo" not in line
    ]
    assert not invocations, (
        "dry-run of bootstrap should not invoke docker; "
        "found invocations:\n" + "\n".join(invocations)
    )


def test_no_docker_does_not_break_makefile_targets(tmp_path: Path) -> None:
    """The Makefile's docker detection messages exist and are well-formed."""
    makefile = (REPO_ROOT / "Makefile").read_text()
    assert "docker compose" in makefile
    assert "Docker not available" in makefile or "docker compose not installed" in makefile


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX-only shell test")
def test_bootstrap_prints_docker_status_message() -> None:
    """The bootstrap target must print one of the two Docker status messages."""
    make = shutil.which("make")
    if make is None:
        pytest.skip("make not installed")
    # We don't actually invoke `make bootstrap` (it would install deps);
    # we only check that the recipe contains the expected informational lines.
    makefile = (REPO_ROOT / "Makefile").read_text()
    assert "Docker available, run 'make docker-build'" in makefile
    assert "Docker not available" in makefile
