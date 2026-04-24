"""Decompilation helpers for BBOverLoad.

Supports two modes:
  * smali  – uses apktool to decode resources and smali bytecode.
  * java   – uses jadx to produce readable Java source code.
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


def decompile_smali(
    apk_path: Path,
    output_dir: Path,
    *,
    decode_resources: bool = True,
) -> Path:
    """Decompile *apk_path* to smali + resources using apktool.

    Parameters
    ----------
    apk_path:
        Path to the source ``.apk`` file.
    output_dir:
        Directory where the decompiled project will be written.
    decode_resources:
        When *False*, pass ``-r`` to apktool to skip resource decoding.
        Useful when ``res`` decoding fails for obfuscated APKs.

    Returns
    -------
    Path
        The directory containing the decoded project.

    Raises
    ------
    RuntimeError
        If apktool is not on PATH or exits with a non-zero code.
    FileNotFoundError
        If *apk_path* does not exist.
    """
    apk_path = Path(apk_path).resolve()
    if not apk_path.is_file():
        raise FileNotFoundError(f"APK not found: {apk_path}")

    output_dir = Path(output_dir).resolve()
    apktool = _require_tool("apktool")

    cmd = [apktool, "d", str(apk_path), "-o", str(output_dir), "-f"]
    if not decode_resources:
        cmd.append("-r")

    logger.info("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"apktool exited with code {result.returncode}:\n{result.stderr}"
        )

    logger.info("Smali decompilation complete → %s", output_dir)
    return output_dir


def decompile_java(
    apk_path: Path,
    output_dir: Path,
) -> Path:
    """Decompile *apk_path* to Java source using jadx.

    Parameters
    ----------
    apk_path:
        Path to the source ``.apk`` file.
    output_dir:
        Directory where the Java sources will be written.

    Returns
    -------
    Path
        The directory containing the Java source tree.

    Raises
    ------
    RuntimeError
        If jadx is not on PATH or exits with a non-zero code.
    FileNotFoundError
        If *apk_path* does not exist.
    """
    apk_path = Path(apk_path).resolve()
    if not apk_path.is_file():
        raise FileNotFoundError(f"APK not found: {apk_path}")

    output_dir = Path(output_dir).resolve()
    jadx = _require_tool("jadx")

    cmd = [jadx, "-d", str(output_dir), str(apk_path)]

    logger.info("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"jadx exited with code {result.returncode}:\n{result.stderr}"
        )

    logger.info("Java decompilation complete → %s", output_dir)
    return output_dir


def decompile(
    apk_path: Path,
    output_dir: Path | None = None,
    mode: str = "smali",
    *,
    decode_resources: bool = True,
) -> Path:
    """High-level entry point for decompilation.

    Parameters
    ----------
    apk_path:
        Path to the ``.apk`` file to decompile.
    output_dir:
        Destination directory.  Defaults to ``output/<apk_stem>/``.
    mode:
        ``"smali"`` (default) or ``"java"``.
    decode_resources:
        Passed through to :func:`decompile_smali` (ignored in java mode).

    Returns
    -------
    Path
        Directory containing the decompiled project.
    """
    apk_path = Path(apk_path)
    if output_dir is None:
        output_dir = Path("output") / apk_path.stem

    mode = mode.lower()
    if mode == "smali":
        return decompile_smali(apk_path, output_dir, decode_resources=decode_resources)
    if mode == "java":
        return decompile_java(apk_path, output_dir)
    raise ValueError(f"Unknown decompile mode '{mode}'. Choose 'smali' or 'java'.")
