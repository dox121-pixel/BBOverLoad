"""Recompilation helpers for BBOverLoad.

Uses apktool to rebuild a decoded smali/resource project into a new APK.

XAPK support:
  When *project_dir* was produced by :func:`bboverload.decompile.decompile_xapk`
  (i.e. it contains multiple apktool sub-projects), :func:`recompile_xapk`
  rebuilds every sub-project and packages the resulting APKs together with the
  original ``manifest.json`` and ``icon.png`` into a new ``.xapk`` archive.
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


def recompile_xapk(
    xapk_project_dir: Path,
    output_dir: Path | None = None,
) -> Path:
    """Rebuild all split APK projects inside an XAPK project directory into a
    new ``.xapk`` archive.

    The *xapk_project_dir* is expected to be the directory that was produced by
    :func:`bboverload.decompile.decompile_xapk` – it must contain at least one
    apktool sub-project (a directory with ``apktool.yml``) and optionally a
    ``manifest.json`` and ``icon.png``.

    Each sub-project is recompiled with apktool.  The rebuilt APKs are then
    zipped together with the metadata files to produce a ``.xapk`` file.

    Parameters
    ----------
    xapk_project_dir:
        Root directory produced by :func:`~bboverload.decompile.decompile_xapk`.
    output_dir:
        Directory where the rebuilt ``.xapk`` will be placed.
        Defaults to ``<xapk_project_dir>/dist/``.

    Returns
    -------
    Path
        Path to the rebuilt ``.xapk`` archive.

    Raises
    ------
    RuntimeError
        If apktool is not on PATH or any sub-project fails to build.
    FileNotFoundError
        If *xapk_project_dir* does not exist or contains no apktool projects.
    """
    xapk_project_dir = Path(xapk_project_dir).resolve()
    if not xapk_project_dir.is_dir():
        raise FileNotFoundError(f"Project directory not found: {xapk_project_dir}")

    # Discover apktool sub-projects (directories that contain apktool.yml)
    sub_projects = sorted(
        p.parent
        for p in xapk_project_dir.rglob("apktool.yml")
        if p.parent != xapk_project_dir
    )
    if not sub_projects:
        raise FileNotFoundError(
            f"No apktool sub-projects found inside '{xapk_project_dir}'.  "
            "Make sure this directory was produced by 'bboverload decompile' on an XAPK."
        )

    if output_dir is None:
        output_dir = xapk_project_dir / "dist"
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    built_apks: list[Path] = []
    for sub in sub_projects:
        logger.info("Recompiling sub-project: %s", sub.name)
        apk = recompile(sub, output_dir=output_dir / sub.name)
        built_apks.append(apk)

    if not built_apks:
        raise RuntimeError("No APKs were successfully built.")

    # Determine output XAPK filename from manifest.json or directory name
    manifest_path = xapk_project_dir / "manifest.json"
    xapk_name = xapk_project_dir.name
    total_size = 0

    if manifest_path.is_file():
        with open(manifest_path, encoding="utf-8") as fh:
            manifest: dict = json.load(fh)
        pkg = manifest.get("package_name", xapk_name)
        ver = manifest.get("version_name", "")
        xapk_name = f"{pkg}_{ver}" if ver else pkg
        # Update total_size in the manifest
        total_size = sum(p.stat().st_size for p in built_apks)
        manifest["total_size"] = total_size
    else:
        manifest = {}

    xapk_out = output_dir / f"{xapk_name}.xapk"

    with zipfile.ZipFile(xapk_out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Write rebuilt APKs
        for apk in built_apks:
            zf.write(apk, apk.name)
        # Write updated manifest
        if manifest:
            zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        # Write icon if present
        icon_src = xapk_project_dir / "icon.png"
        if icon_src.is_file():
            zf.write(icon_src, "icon.png")

    logger.info("XAPK repackaged → %s", xapk_out)
    return xapk_out
