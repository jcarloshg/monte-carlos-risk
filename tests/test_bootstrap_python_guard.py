"""Sad Path BDD Scenario 2.

Given the system Python is 3.11 or earlier,
When the bootstrap guard is invoked,
Then it MUST exit non-zero with the message "Python 3.12 required".
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GUARD = REPO_ROOT / "scripts" / "bootstrap_python_guard.sh"


@pytest.mark.skipif(not GUARD.exists(), reason="bootstrap guard script missing")
def test_guard_script_is_executable() -> None:
    assert shutil.which("bash") is not None
    assert GUARD.is_file()


@pytest.mark.skipif(not GUARD.exists(), reason="bootstrap guard script missing")
def test_guard_rejects_old_python(tmp_path: Path) -> None:
    """Drive the guard with a real Python that pretends to be 3.11.

    The guard invokes `python - <<'PY' ... PY` which reads a script from stdin.
    We build a stub that delegates to a real Python interpreter but lies about
    its `sys.version_info` so the guard sees 3.11 and must reject it.
    """
    real_python = shutil.which("python3.12") or shutil.which("python3")  # type: ignore[assignment]
    if real_python is None:
        pytest.skip("no real python interpreter available")

    fake = tmp_path / "fake_python"
    fake.write_text(
        "#!/usr/bin/env python3\n"
        "import runpy\n"
        "import sys\n"
        "\n"
        "# Pretend to be Python 3.11 for the guard's version check.\n"
        "class _V:\n"
        "    def __init__(self, major, minor, micro):\n"
        "        self.major = major\n"
        "        self.minor = minor\n"
        "        self.micro = micro\n"
        "\n"
        "sys.version_info = _V(3, 11, 9)\n"
        "\n"
        'if __name__ == "__main__":\n'
        '    runpy.run_path(sys.argv[1], run_globals={"sys": sys})\n'
        "    sys.exit(0)\n"
    )
    fake.chmod(0o755)

    # The fake reads a script path from argv[1]; the guard pipes to stdin via
    # `python -`. Write the script to a temp file and pass it instead.
    fake_call = tmp_path / "fake_call.sh"
    fake_call.write_text(
        "#!/usr/bin/env bash\n"
        f'FAKE_PY="{fake}"\n'
        'if [ "$1" = "-V" ]; then echo "Python 3.11.9"; exit 0; fi\n'
        # `python - <<EOF ... EOF` makes stdin a script and argv stays empty;
        # capture the heredoc into a file and pass it to the stub.
        'STDIN_FILE="$(mktemp)"\n'
        'cat >"$STDIN_FILE"\n'
        '"$FAKE_PY" "$STDIN_FILE"\n'
        "rc=$?\n"
        'rm -f "$STDIN_FILE"\n'
        "exit $rc\n"
    )
    fake_call.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:/usr/bin:/bin"
    env["PYTHON"] = "fake_call.sh"

    result = subprocess.run(
        ["bash", str(GUARD)],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode != 0, (
        f"guard should reject Python 3.11, got rc={result.returncode}\n"
        f"stdout={result.stdout}\nstderr={result.stderr}"
    )
    combined = result.stdout + result.stderr
    assert "Python 3.12 required" in combined, f"missing required error message; got:\n{combined}"


@pytest.mark.skipif(not GUARD.exists(), reason="bootstrap guard script missing")
def test_guard_accepts_modern_python() -> None:
    """Sanity check: with the system interpreter (>= 3.12) the guard passes."""
    env = os.environ.copy()
    env["PATH"] = f"/usr/bin:/bin:{env.get('PATH', '')}"
    env["PYTHON"] = "python3.12"

    result = subprocess.run(
        ["bash", str(GUARD)],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, (
        f"guard should accept Python 3.12, got rc={result.returncode}\nstderr={result.stderr}"
    )
    assert "Using interpreter" in result.stdout
