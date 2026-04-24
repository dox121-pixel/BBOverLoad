"""Recompilation helpers for BBOverLoad.

Uses apktool to rebuild a decoded smali/resource project into a new APK.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def _require_tool(name: str) -> str:
    """Return the full path to *name* or raise RuntimeError if not found."""
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(
            f"'{name}' was not found on PATH.  "
            f"Run 'bash scripts/install_tools.sh' to install required tools."
        )
    return path


def recompile(
    project_dir: Path,
    output_dir: Path | None = None,
) -> Path:
    """Rebuild a decoded apktool project directory into an APK.

    Parameters
    ----------
    project_dir:
        Root directory of the decoded project (must contain ``apktool.yml``).
    output_dir:
        Where to place the rebuilt APK.  Defaults to ``<project_dir>/dist/``.

    Returns
    -------
    Path
        Path to the newly built APK file.

    Raises
    ------
    RuntimeError
        If apktool is not on PATH or exits with a non-zero code.
    FileNotFoundError
        If *project_dir* does not exist or is not an apktool project.
    """
    project_dir = Path(project_dir).resolve()
    if not project_dir.is_dir():
        raise FileNotFoundError(f"Project directory not found: {project_dir}")

    apktool_yml = project_dir / "apktool.yml"
    if not apktool_yml.is_file():
        raise FileNotFoundError(
            f"'{apktool_yml}' not found.  "
            f"'{project_dir}' does not look like an apktool project."
        )

    if output_dir is None:
        output_dir = project_dir / "dist"
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    apktool = _require_tool("apktool")
    cmd = [apktool, "b", str(project_dir), "-o", str(output_dir / f"{project_dir.name}.apk")]

    logger.info("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"apktool exited with code {result.returncode}:\n{result.stderr}"
        )

    built_apk = output_dir / f"{project_dir.name}.apk"
    logger.info("Recompilation complete → %s", built_apk)
    return built_apk
