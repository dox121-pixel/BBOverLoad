"""Tests for bboverload.sign."""

from __future__ import annotations

import shutil
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from bboverload.sign import sign


class TestSign:
    def test_missing_apk_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="APK not found"):
            sign(tmp_path / "missing.apk")

    def test_missing_custom_keystore_raises(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")
        with pytest.raises(FileNotFoundError, match="Keystore not found"):
            sign(apk, keystore=tmp_path / "missing.jks")

    def test_custom_keystore_without_alias_raises(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")
        ks = tmp_path / "my.jks"
        ks.write_bytes(b"fake-keystore")
        with pytest.raises(ValueError, match="--alias is required"):
            sign(apk, keystore=ks)

    def test_default_output_path_is_signed_apk(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("shutil.which", return_value="/usr/bin/jarsigner"), \
             patch("bboverload.sign._ensure_debug_keystore",
                   return_value=tmp_path / "debug.keystore"), \
             patch("subprocess.run", return_value=mock_result):
            returned = sign(apk)

        assert returned.name == "game_signed.apk"
        assert returned.parent == tmp_path

    def test_custom_output_path(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")
        out = tmp_path / "signed" / "output.apk"

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("shutil.which", return_value="/usr/bin/jarsigner"), \
             patch("bboverload.sign._ensure_debug_keystore",
                   return_value=tmp_path / "debug.keystore"), \
             patch("subprocess.run", return_value=mock_result):
            returned = sign(apk, output_path=out)

        assert returned.resolve() == out.resolve()

    def test_jarsigner_failure_raises(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "jarsigner error"

        with patch("shutil.which", return_value="/usr/bin/jarsigner"), \
             patch("bboverload.sign._ensure_debug_keystore",
                   return_value=tmp_path / "debug.keystore"), \
             patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="jarsigner exited with code 1"):
                sign(apk)

    def test_missing_jarsigner_raises(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")

        with patch("shutil.which", return_value=None), \
             patch("bboverload.sign._ensure_debug_keystore",
                   return_value=tmp_path / "debug.keystore"):
            with pytest.raises(RuntimeError, match="not found on PATH"):
                sign(apk)

    def test_calls_jarsigner_with_keystore_args(self, tmp_path):
        apk = tmp_path / "game.apk"
        apk.write_bytes(b"PK\x03\x04")
        ks = tmp_path / "my.jks"
        ks.write_bytes(b"fake-keystore")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("shutil.which", return_value="/usr/bin/jarsigner"), \
             patch("subprocess.run", return_value=mock_result) as mock_run:
            sign(apk, keystore=ks, alias="mykey", storepass="secret", keypass="pass")

        call_args = mock_run.call_args[0][0]
        assert "-keystore" in call_args
        assert str(ks.resolve()) in call_args
        assert "mykey" in call_args
        assert "secret" in call_args
        assert "pass" in call_args
