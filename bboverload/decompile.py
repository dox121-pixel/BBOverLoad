"""Decompilation helpers for BBOverLoad.

Supports two modes:
  * smali  – uses apktool to decode resources and smali bytecode.
  * java   – uses jadx to produce readable Java source code.

XAPK support:
  XAPK files (used by APKPure) are ZIP archives that contain one or more APK
  split files plus a ``manifest.json``.  When an ``.xapk`` path is passed to
  :func:`decompile`, the archive is first extracted and every APK inside is
  decompiled into its own sub-directory of *output_dir*.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import zipfile
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


def extract_xapk(
    xapk_path: Path,
    extract_dir: Path,
) -> tuple[list[Path], dict]:
    """Extract an XAPK archive and return the list of APK paths and manifest.

    An XAPK is a ZIP file produced by APKPure that contains one or more APK
    split files and a ``manifest.json``.  This function extracts everything
    into *extract_dir* and returns the APK paths and the parsed manifest dict.

    Parameters
    ----------
    xapk_path:
        Path to the ``.xapk`` file.
    extract_dir:
        Directory into which the archive is extracted.

    Returns
    -------
    tuple[list[Path], dict]
        A list of extracted APK paths and the parsed ``manifest.json`` dict.

    Raises
    ------
    FileNotFoundError
        If *xapk_path* does not exist.
    ValueError
        If the file is not a valid ZIP / XAPK archive.
    """
    xapk_path = Path(xapk_path).resolve()
    if not xapk_path.is_file():
        raise FileNotFoundError(f"XAPK not found: {xapk_path}")

    extract_dir = Path(extract_dir).resolve()
    extract_dir.mkdir(parents=True, exist_ok=True)

    if not zipfile.is_zipfile(xapk_path):
        raise ValueError(f"'{xapk_path}' is not a valid ZIP/XAPK file.")

    with zipfile.ZipFile(xapk_path, "r") as zf:
        zf.extractall(extract_dir)

    manifest: dict = {}
    manifest_path = extract_dir / "manifest.json"
    if manifest_path.is_file():
        with open(manifest_path, encoding="utf-8") as fh:
            manifest = json.load(fh)

    apk_paths = sorted(extract_dir.glob("*.apk"))
    logger.info("Extracted %d APK(s) from XAPK → %s", len(apk_paths), extract_dir)
    return apk_paths, manifest


def decompile_xapk(
    xapk_path: Path,
    output_dir: Path,
    mode: str = "smali",
    *,
    decode_resources: bool = True,
) -> Path:
    """Decompile all APKs inside an XAPK archive.

    The XAPK is first extracted into ``<output_dir>/_extracted/`` and then
    each APK is decompiled into its own sub-directory inside *output_dir*.
    The XAPK ``manifest.json`` and ``icon.png`` (if present) are copied to
    *output_dir* as well.

    Parameters
    ----------
    xapk_path:
        Path to the ``.xapk`` file.
    output_dir:
        Root output directory.  Sub-directories are created per APK.
    mode:
        ``"smali"`` (default) or ``"java"``.
    decode_resources:
        Passed through to :func:`decompile_smali` (ignored in java mode).

    Returns
    -------
    Path
        The *output_dir* containing all decompiled sub-projects.

    Raises
    ------
    RuntimeError
        If apktool / jadx is not on PATH.
    FileNotFoundError
        If *xapk_path* does not exist.
    """
    xapk_path = Path(xapk_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    extract_dir = output_dir / "_extracted"
    apk_paths, manifest = extract_xapk(xapk_path, extract_dir)

    # Copy metadata files to output root for reference
    for name in ("manifest.json", "icon.png"):
        src = extract_dir / name
        if src.is_file():
            shutil.copy2(src, output_dir / name)

    mode = mode.lower()
    for apk_path in apk_paths:
        stem = apk_path.stem
        if mode == "java":
            apk_out = output_dir / f"{stem}-java"
            decompile_java(apk_path, apk_out)
        else:
            apk_out = output_dir / stem
            decompile_smali(apk_path, apk_out, decode_resources=decode_resources)

    logger.info("XAPK decompilation complete → %s", output_dir)
    return output_dir


def decompile(
    apk_path: Path,
    output_dir: Path | None = None,
    mode: str = "smali",
    *,
    decode_resources: bool = True,
) -> Path:
    """High-level entry point for decompilation.

    Accepts both ``.apk`` and ``.xapk`` input files.  When given an XAPK
    file, all split APKs inside are decompiled via :func:`decompile_xapk`.

    Parameters
    ----------
    apk_path:
        Path to the ``.apk`` or ``.xapk`` file to decompile.
    output_dir:
        Destination directory.  Defaults to ``output/<apk_stem>/``.
    mode:
        ``"smali"`` (default) or ``"java"``.
    decode_resources:
        Passed through to :func:`decompile_smali` (ignored in java mode).

    Returns
    -------
    Path
        Directory containing the decompiled project(s).
    """
    apk_path = Path(apk_path)
    if output_dir is None:
        output_dir = Path("output") / apk_path.stem

    # XAPK path – decompile every split APK inside
    if apk_path.suffix.lower() == ".xapk":
        return decompile_xapk(
            apk_path, output_dir, mode=mode, decode_resources=decode_resources
        )

    mode = mode.lower()
    if mode == "smali":
        return decompile_smali(apk_path, output_dir, decode_resources=decode_resources)
    if mode == "java":
        return decompile_java(apk_path, output_dir)
    raise ValueError(f"Unknown decompile mode '{mode}'. Choose 'smali' or 'java'.")
