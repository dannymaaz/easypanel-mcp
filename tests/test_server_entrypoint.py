"""Regression tests for launching the MCP server entrypoint."""

import os
import subprocess
import sys
from pathlib import Path


def _server_env() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "EASYPANEL_URL": "http://test.com",
            "EASYPANEL_API_KEY": "test_token",
        }
    )
    return env


def test_server_script_resolves_project_imports_from_external_cwd(tmp_path: Path) -> None:
    """Direct execution must resolve repo-local imports outside the repo cwd."""
    repo_root = Path(__file__).resolve().parents[1]
    server_path = repo_root / "src" / "server.py"

    code = (
        "import runpy; "
        f"runpy.run_path({str(server_path)!r}, run_name='entrypoint_import_test')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=_server_env(),
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_installed_server_imports_from_external_cwd(tmp_path: Path) -> None:
    """The installed package must include both src and the root config module."""
    result = subprocess.run(
        [sys.executable, "-c", "import config; import src.server"],
        cwd=tmp_path,
        env=_server_env(),
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )

    assert result.returncode == 0, result.stderr
