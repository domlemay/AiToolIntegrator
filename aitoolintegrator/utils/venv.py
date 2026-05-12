"""Virtual environment creation and management utilities."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from aitoolintegrator.utils.logger import get_logger

logger = get_logger(__name__)


def create_venv(venv_dir: Path) -> None:
    """Create a Python virtual environment at the given path.

    Args:
        venv_dir: Target path for the new venv.

    Raises:
        RuntimeError: If venv creation fails.
    """
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.debug("Created venv at %s", venv_dir)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Failed to create venv at {venv_dir}: {exc.stderr}") from exc


def get_pip(venv_dir: Path) -> Path:
    """Return the pip executable path for a given venv.

    Args:
        venv_dir: Path to the virtual environment.

    Returns:
        Absolute path to the pip executable.
    """
    if sys.platform == "win32":
        pip = venv_dir / "Scripts" / "pip.exe"
    else:
        pip = venv_dir / "bin" / "pip"
    return pip


def get_python(venv_dir: Path) -> Path:
    """Return the python executable path for a given venv.

    Args:
        venv_dir: Path to the virtual environment.

    Returns:
        Absolute path to the python executable.
    """
    if sys.platform == "win32":
        python = venv_dir / "Scripts" / "python.exe"
    else:
        python = venv_dir / "bin" / "python"
    return python


def install_requirements(venv_dir: Path, requirements_file: Path) -> None:
    """Install requirements into a virtual environment.

    Args:
        venv_dir: Path to the virtual environment.
        requirements_file: Path to requirements.txt.

    Raises:
        RuntimeError: If pip install fails.
        FileNotFoundError: If requirements.txt does not exist.
    """
    if not requirements_file.exists():
        raise FileNotFoundError(f"Requirements file not found: {requirements_file}")

    pip = get_pip(venv_dir)
    if not pip.exists():
        raise RuntimeError(f"pip not found in venv: {pip}")

    try:
        subprocess.run(
            [str(pip), "install", "-r", str(requirements_file), "--quiet"],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.debug("Installed requirements from %s", requirements_file)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"pip install failed: {exc.stderr}") from exc


def venv_exists(venv_dir: Path) -> bool:
    """Check whether a virtual environment directory exists and is valid.

    Args:
        venv_dir: Path to the virtual environment.

    Returns:
        True if the venv looks valid, False otherwise.
    """
    return venv_dir.exists() and get_python(venv_dir).exists()
