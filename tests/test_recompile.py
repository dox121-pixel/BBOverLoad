"""Tests for bboverload.recompile."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bboverload.recompile import recompile


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
