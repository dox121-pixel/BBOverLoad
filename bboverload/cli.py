"""Command-line interface for BBOverLoad."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

from bboverload import __version__
from bboverload.decompile import decompile
from bboverload.recompile import recompile, recompile_xapk
from bboverload.sign import sign as _sign

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stderr,
)


@click.group()
@click.version_option(__version__, prog_name="bboverload")
def cli() -> None:
    """BBOverLoad – APK decompilation and recompilation toolkit."""


# ---------------------------------------------------------------------------
# decompile
# ---------------------------------------------------------------------------

@cli.command("decompile")
@click.argument("apk_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--mode",
    type=click.Choice(["smali", "java"], case_sensitive=False),
    default="smali",
    show_default=True,
    help="Decompile mode: 'smali' uses apktool, 'java' uses jadx.",
)
@click.option(
    "--output",
    "output_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Output directory (default: output/<apk_stem>/).",
)
@click.option(
    "--no-res",
    "no_res",
    is_flag=True,
    default=False,
    help="Skip resource decoding (smali mode only).",
)
def decompile_cmd(apk_path: Path, mode: str, output_dir: Path | None, no_res: bool) -> None:
    """Decompile APK_PATH (or an XAPK archive) into an editable project.

    When an XAPK file is supplied every split APK it contains is decompiled
    into its own sub-directory of the output directory.
    """
    try:
        result = decompile(
            apk_path,
            output_dir=output_dir,
            mode=mode,
            decode_resources=not no_res,
        )
        click.echo(f"✓ Decompiled to: {result}")
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        click.echo(f"✗ {exc}", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# recompile
# ---------------------------------------------------------------------------

@cli.command("recompile")
@click.argument(
    "project_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--output",
    "output_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Output directory for the rebuilt APK (default: <PROJECT_DIR>/dist/).",
)
def recompile_cmd(project_dir: Path, output_dir: Path | None) -> None:
    """Recompile a modified PROJECT_DIR back into an APK."""
    try:
        result = recompile(project_dir, output_dir=output_dir)
        click.echo(f"✓ Rebuilt APK: {result}")
    except (RuntimeError, FileNotFoundError) as exc:
        click.echo(f"✗ {exc}", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# recompile-xapk
# ---------------------------------------------------------------------------

@cli.command("recompile-xapk")
@click.argument(
    "xapk_project_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--output",
    "output_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Output directory for the rebuilt XAPK (default: <XAPK_PROJECT_DIR>/dist/).",
)
def recompile_xapk_cmd(xapk_project_dir: Path, output_dir: Path | None) -> None:
    """Repackage an XAPK_PROJECT_DIR (from 'decompile' on an XAPK) back into a .xapk archive.

    All apktool sub-projects inside XAPK_PROJECT_DIR are rebuilt with apktool
    and the resulting APKs are packaged together with the original manifest.json
    and icon.png into a new .xapk file.
    """
    try:
        result = recompile_xapk(xapk_project_dir, output_dir=output_dir)
        click.echo(f"✓ Rebuilt XAPK: {result}")
    except (RuntimeError, FileNotFoundError) as exc:
        click.echo(f"✗ {exc}", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# sign
# ---------------------------------------------------------------------------

@cli.command("sign")
@click.argument("apk_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--keystore",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Path to a .jks / .keystore file (default: built-in debug key).",
)
@click.option("--alias", default=None, help="Key alias.")
@click.option("--storepass", default=None, help="Keystore password.")
@click.option("--keypass", default=None, help="Key password.")
@click.option(
    "--output",
    "output_path",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Output path for the signed APK (default: <APK_PATH>_signed.apk).",
)
def sign_cmd(
    apk_path: Path,
    keystore: Path | None,
    alias: str | None,
    storepass: str | None,
    keypass: str | None,
    output_path: Path | None,
) -> None:
    """Sign APK_PATH with jarsigner."""
    try:
        result = _sign(
            apk_path,
            output_path=output_path,
            keystore=keystore,
            alias=alias,
            storepass=storepass,
            keypass=keypass,
        )
        click.echo(f"✓ Signed APK: {result}")
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        click.echo(f"✗ {exc}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
