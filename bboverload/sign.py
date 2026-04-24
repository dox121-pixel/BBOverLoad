"""APK signing helpers for BBOverLoad.

Supports signing with:
  * A user-supplied JKS / keystore file.
  * A built-in debug keystore (generated on first use via keytool).
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

# Location of the auto-generated debug keystore
_DEBUG_KEYSTORE_DIR = Path.home() / ".bboverload"
_DEBUG_KEYSTORE_PATH = _DEBUG_KEYSTORE_DIR / "debug.keystore"
_DEBUG_ALIAS = "androiddebugkey"
_DEBUG_STOREPASS = "android"
_DEBUG_KEYPASS = "android"


def _require_tool(name: str) -> str:
    """Return the full path to *name* or raise RuntimeError if not found."""
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(
            f"'{name}' was not found on PATH.  "
            f"Ensure the JDK is installed and on your PATH."
        )
    return path


def _ensure_debug_keystore() -> Path:
    """Create a debug keystore the first time it is needed."""
    if _DEBUG_KEYSTORE_PATH.is_file():
        return _DEBUG_KEYSTORE_PATH

    _DEBUG_KEYSTORE_DIR.mkdir(parents=True, exist_ok=True)
    keytool = _require_tool("keytool")
    cmd = [
        keytool, "-genkeypair",
        "-keystore", str(_DEBUG_KEYSTORE_PATH),
        "-alias", _DEBUG_ALIAS,
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "10000",
        "-storepass", _DEBUG_STOREPASS,
        "-keypass", _DEBUG_KEYPASS,
        "-dname", "CN=Android Debug,O=Android,C=US",
    ]
    logger.info("Generating debug keystore at %s", _DEBUG_KEYSTORE_PATH)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"keytool exited with code {result.returncode}:\n{result.stderr}"
        )
    return _DEBUG_KEYSTORE_PATH


def sign(
    apk_path: Path,
    output_path: Path | None = None,
    *,
    keystore: Path | None = None,
    alias: str | None = None,
    storepass: str | None = None,
    keypass: str | None = None,
) -> Path:
    """Sign an APK with jarsigner.

    Parameters
    ----------
    apk_path:
        Path to the unsigned APK.
    output_path:
        Destination for the signed APK.  Defaults to
        ``<apk_path.stem>_signed.apk`` in the same directory.
    keystore:
        Path to a JKS/keystore file.  Uses the built-in debug key if omitted.
    alias:
        Key alias inside the keystore.
    storepass:
        Keystore password.
    keypass:
        Key password.

    Returns
    -------
    Path
        Path to the signed APK.

    Raises
    ------
    RuntimeError
        If jarsigner is not on PATH or exits with a non-zero code.
    FileNotFoundError
        If *apk_path* does not exist.
    """
    apk_path = Path(apk_path).resolve()
    if not apk_path.is_file():
        raise FileNotFoundError(f"APK not found: {apk_path}")

    # Resolve keystore / credentials
    if keystore is None:
        keystore = _ensure_debug_keystore()
        alias = alias or _DEBUG_ALIAS
        storepass = storepass or _DEBUG_STOREPASS
        keypass = keypass or _DEBUG_KEYPASS
    else:
        keystore = Path(keystore).resolve()
        if not keystore.is_file():
            raise FileNotFoundError(f"Keystore not found: {keystore}")
        if alias is None:
            raise ValueError("--alias is required when a custom keystore is provided.")
        storepass = storepass or ""
        keypass = keypass or ""

    # Determine output path
    if output_path is None:
        output_path = apk_path.parent / f"{apk_path.stem}_signed{apk_path.suffix}"
    else:
        output_path = Path(output_path).resolve()

    jarsigner = _require_tool("jarsigner")

    # Ensure destination directory exists, then copy APK and sign in-place
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(apk_path, output_path)

    cmd = [
        jarsigner,
        "-keystore", str(keystore),
        "-storepass", storepass,
        "-keypass", keypass,
        "-signedjar", str(output_path),
        str(output_path),
        alias,
    ]

    logger.info("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"jarsigner exited with code {result.returncode}:\n{result.stderr}"
        )

    logger.info("Signing complete → %s", output_path)
    return output_path
