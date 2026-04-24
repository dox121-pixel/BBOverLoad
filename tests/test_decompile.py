"""Tests for bboverload.decompile."""

from __future__ import annotations

import io
import json
import subprocess
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bboverload.decompile import (
    decompile,
    decompile_java,
    decompile_smali,
    decompile_xapk,
    extract_xapk,
)


class TestRequireTool:
    def test_missing_tool_raises(self):
        from bboverload.decompile import _require_tool
        with patch("shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="not found on PATH"):
                _require_tool("nonexistent_tool")

    def test_found_tool_returns_path(self):
        from bboverload.decompile import _require_tool
        with patch("shutil.which", return_value="/usr/bin/apktool"):
            assert _require_tool("apktool") == "/usr/bin/apktool"


class TestDecompileSmali:
    def test_missing_apk_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="APK not found"):
            decompile_smali(tmp_path / "missing.apk", tmp_path / "out")

    def test_calls_apktool_with_correct_args(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")  # minimal ZIP magic
        out = tmp_path / "out"

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("shutil.which", return_value="/usr/bin/apktool"), \
             patch("subprocess.run", return_value=mock_result) as mock_run:
            returned = decompile_smali(apk, out)

        call_args = mock_run.call_args[0][0]
        assert "apktool" in call_args[0]
        assert "d" in call_args
        assert "-f" in call_args
        assert str(apk.resolve()) in call_args
        assert returned == out.resolve()

    def test_no_res_flag_added(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")
        out = tmp_path / "out"

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("shutil.which", return_value="/usr/bin/apktool"), \
             patch("subprocess.run", return_value=mock_result) as mock_run:
            decompile_smali(apk, out, decode_resources=False)

        call_args = mock_run.call_args[0][0]
        assert "-r" in call_args

    def test_apktool_failure_raises(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")
        out = tmp_path / "out"

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "some error"

        with patch("shutil.which", return_value="/usr/bin/apktool"), \
             patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="apktool exited with code 1"):
                decompile_smali(apk, out)


class TestDecompileJava:
    def test_missing_apk_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="APK not found"):
            decompile_java(tmp_path / "missing.apk", tmp_path / "out")

    def test_calls_jadx_with_correct_args(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")
        out = tmp_path / "out"

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("shutil.which", return_value="/usr/bin/jadx"), \
             patch("subprocess.run", return_value=mock_result) as mock_run:
            returned = decompile_java(apk, out)

        call_args = mock_run.call_args[0][0]
        assert "jadx" in call_args[0]
        assert "-d" in call_args
        assert str(apk.resolve()) in call_args
        assert returned == out.resolve()

    def test_jadx_failure_raises(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")
        out = tmp_path / "out"

        mock_result = MagicMock()
        mock_result.returncode = 2
        mock_result.stderr = "jadx error"

        with patch("shutil.which", return_value="/usr/bin/jadx"), \
             patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="jadx exited with code 2"):
                decompile_java(apk, out)


class TestDecompileDispatch:
    def test_default_mode_is_smali(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")

        with patch("bboverload.decompile.decompile_smali") as mock_smali:
            mock_smali.return_value = tmp_path / "out"
            decompile(apk)
        mock_smali.assert_called_once()

    def test_java_mode_dispatches_to_decompile_java(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")

        with patch("bboverload.decompile.decompile_java") as mock_java:
            mock_java.return_value = tmp_path / "out"
            decompile(apk, mode="java")
        mock_java.assert_called_once()

    def test_invalid_mode_raises(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")
        with pytest.raises(ValueError, match="Unknown decompile mode"):
            decompile(apk, mode="bytecode")

    def test_default_output_dir_uses_stem(self, tmp_path, monkeypatch):
        apk = tmp_path / "mygame.apk"
        apk.write_bytes(b"PK\x03\x04")
        monkeypatch.chdir(tmp_path)

        with patch("bboverload.decompile.decompile_smali") as mock_smali:
            mock_smali.return_value = tmp_path / "output" / "mygame"
            decompile(apk)

        called_output_dir = mock_smali.call_args[0][1]
        assert called_output_dir == Path("output") / "mygame"

    def test_xapk_dispatches_to_decompile_xapk(self, tmp_path):
        """decompile() must call decompile_xapk for .xapk files."""
        xapk = tmp_path / "game.xapk"
        xapk.write_bytes(b"PK\x03\x04")

        with patch("bboverload.decompile.decompile_xapk") as mock_xapk:
            mock_xapk.return_value = tmp_path / "out"
            decompile(xapk)
        mock_xapk.assert_called_once()


def _make_xapk(path: Path, apk_names: list[str], include_manifest: bool = True) -> None:
    """Helper: build a minimal XAPK (ZIP) with stub APKs and optional manifest."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name in apk_names:
            zf.writestr(name, b"PK\x03\x04stub")
        if include_manifest:
            manifest = {
                "package_name": "com.example.test",
                "version_name": "1.0",
                "split_apks": [{"file": n, "id": n.replace(".apk", "")} for n in apk_names],
            }
            zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("icon.png", b"\x89PNG\r\n\x1a\n")
    path.write_bytes(buf.getvalue())


class TestExtractXapk:
    def test_missing_xapk_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="XAPK not found"):
            extract_xapk(tmp_path / "missing.xapk", tmp_path / "out")

    def test_invalid_zip_raises(self, tmp_path):
        bad = tmp_path / "bad.xapk"
        bad.write_bytes(b"not a zip")
        with pytest.raises(ValueError, match="not a valid ZIP"):
            extract_xapk(bad, tmp_path / "out")

    def test_extracts_apks_and_returns_paths(self, tmp_path):
        xapk = tmp_path / "game.xapk"
        _make_xapk(xapk, ["base.apk", "config.arm64.apk"])

        apk_paths, manifest = extract_xapk(xapk, tmp_path / "out")

        assert len(apk_paths) == 2
        assert all(p.suffix == ".apk" for p in apk_paths)
        assert manifest["package_name"] == "com.example.test"

    def test_no_manifest_returns_empty_dict(self, tmp_path):
        xapk = tmp_path / "game.xapk"
        _make_xapk(xapk, ["base.apk"], include_manifest=False)

        _, manifest = extract_xapk(xapk, tmp_path / "out")
        assert manifest == {}


class TestDecompileXapk:
    def test_missing_xapk_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            decompile_xapk(tmp_path / "missing.xapk", tmp_path / "out")

    def test_decompiles_all_splits(self, tmp_path):
        xapk = tmp_path / "game.xapk"
        _make_xapk(xapk, ["base.apk", "config.en.apk"])
        out = tmp_path / "out"

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("shutil.which", return_value="/usr/bin/apktool"), \
             patch("subprocess.run", return_value=mock_result) as mock_run:
            returned = decompile_xapk(xapk, out)

        # apktool should have been called once per APK
        assert mock_run.call_count == 2
        assert returned == out

    def test_icon_and_manifest_copied_to_output(self, tmp_path):
        xapk = tmp_path / "game.xapk"
        _make_xapk(xapk, ["base.apk"])
        out = tmp_path / "out"

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("shutil.which", return_value="/usr/bin/apktool"), \
             patch("subprocess.run", return_value=mock_result):
            decompile_xapk(xapk, out)

        assert (out / "manifest.json").is_file()
        assert (out / "icon.png").is_file()
