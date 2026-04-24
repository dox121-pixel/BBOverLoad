"""Tests for bboverload.recompile."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from bboverload.recompile import recompile, recompile_xapk


class TestRecompile:
    def test_missing_project_dir_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="Project directory not found"):
            recompile(tmp_path / "nonexistent")

    def test_no_apktool_yml_raises(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        with pytest.raises(FileNotFoundError, match="apktool.yml"):
            recompile(project_dir)

    def test_calls_apktool_b_with_correct_args(self, tmp_path):
        project_dir = tmp_path / "mygame"
        project_dir.mkdir()
        (project_dir / "apktool.yml").write_text("!!brut.androlib.meta.MetaInfo\n")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("shutil.which", return_value="/usr/bin/apktool"), \
             patch("subprocess.run", return_value=mock_result) as mock_run:
            returned = recompile(project_dir)

        call_args = mock_run.call_args[0][0]
        assert "apktool" in call_args[0]
        assert "b" in call_args
        assert str(project_dir.resolve()) in call_args

        # Returned path should be inside dist/
        assert returned == project_dir.resolve() / "dist" / "mygame.apk"

    def test_custom_output_dir(self, tmp_path):
        project_dir = tmp_path / "mygame"
        project_dir.mkdir()
        (project_dir / "apktool.yml").write_text("!!brut.androlib.meta.MetaInfo\n")
        custom_out = tmp_path / "custom_output"

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("shutil.which", return_value="/usr/bin/apktool"), \
             patch("subprocess.run", return_value=mock_result):
            returned = recompile(project_dir, output_dir=custom_out)

        assert returned == custom_out.resolve() / "mygame.apk"

    def test_apktool_failure_raises(self, tmp_path):
        project_dir = tmp_path / "mygame"
        project_dir.mkdir()
        (project_dir / "apktool.yml").write_text("!!brut.androlib.meta.MetaInfo\n")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "build failed"

        with patch("shutil.which", return_value="/usr/bin/apktool"), \
             patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="apktool exited with code 1"):
                recompile(project_dir)

    def test_missing_apktool_raises(self, tmp_path):
        project_dir = tmp_path / "mygame"
        project_dir.mkdir()
        (project_dir / "apktool.yml").write_text("!!brut.androlib.meta.MetaInfo\n")

        with patch("shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="not found on PATH"):
                recompile(project_dir)


def _make_sub_project(parent: Path, name: str) -> Path:
    """Create a minimal apktool sub-project directory."""
    sub = parent / name
    sub.mkdir(parents=True)
    (sub / "apktool.yml").write_text("!!brut.androlib.meta.MetaInfo\n")
    return sub


class TestRecompileXapk:
    def test_missing_project_dir_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="Project directory not found"):
            recompile_xapk(tmp_path / "nonexistent")

    def test_no_sub_projects_raises(self, tmp_path):
        xapk_dir = tmp_path / "xapk_project"
        xapk_dir.mkdir()
        with pytest.raises(FileNotFoundError, match="No apktool sub-projects"):
            recompile_xapk(xapk_dir)

    def test_builds_each_sub_project(self, tmp_path):
        xapk_dir = tmp_path / "xapk_project"
        xapk_dir.mkdir()
        _make_sub_project(xapk_dir, "base")
        _make_sub_project(xapk_dir, "config.en")

        # Provide a minimal manifest.json
        manifest = {"package_name": "com.example", "version_name": "1.0"}
        (xapk_dir / "manifest.json").write_text(json.dumps(manifest))

        def fake_recompile(project_dir, output_dir=None):
            if output_dir is None:
                output_dir = project_dir / "dist"
            out = Path(output_dir)
            out.mkdir(parents=True, exist_ok=True)
            apk = out / f"{Path(project_dir).name}.apk"
            apk.write_bytes(b"PK\x03\x04")
            return apk

        with patch("bboverload.recompile.recompile", side_effect=fake_recompile) as mock_recompile:
            out_xapk = recompile_xapk(xapk_dir)

        # recompile should have been called once per sub-project
        assert mock_recompile.call_count == 2
        assert out_xapk.suffix == ".xapk"

    def test_output_xapk_is_valid_zip(self, tmp_path):
        xapk_dir = tmp_path / "xapk_project"
        xapk_dir.mkdir()
        _make_sub_project(xapk_dir, "base")

        manifest = {"package_name": "com.example", "version_name": "2.0"}
        (xapk_dir / "manifest.json").write_text(json.dumps(manifest))
        (xapk_dir / "icon.png").write_bytes(b"\x89PNG")

        def fake_recompile(project_dir, output_dir=None):
            if output_dir is None:
                output_dir = project_dir / "dist"
            out = Path(output_dir)
            out.mkdir(parents=True, exist_ok=True)
            apk = out / f"{Path(project_dir).name}.apk"
            apk.write_bytes(b"PK\x03\x04")
            return apk

        with patch("bboverload.recompile.recompile", side_effect=fake_recompile):
            out_xapk = recompile_xapk(xapk_dir)

        assert zipfile.is_zipfile(out_xapk)
        with zipfile.ZipFile(out_xapk) as zf:
            names = zf.namelist()
        assert "manifest.json" in names
        assert "icon.png" in names
