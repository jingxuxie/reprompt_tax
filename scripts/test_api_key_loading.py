#!/usr/bin/env python
"""Regression tests for portable OpenAI API-key loading."""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from run_models import read_api_key


SURFACE_PATHS = [
    Path("README.md"),
    Path("scripts/run_models.py"),
    Path("scripts/judge_outputs.py"),
    Path("scripts/run_repair_prompt_variants.py"),
]


def legacy_local_markers() -> tuple[str, ...]:
    local_user = "es" + "ton"
    workspace = "colm_" + "workshop"
    return (
        "/" + "home" + "/" + local_user,
        workspace,
        "/" + "home" + "/" + local_user + "/" + workspace + "/" + "apikey.txt",
    )


def expect_value_error(call: Callable[[], object], expected_phrase: str) -> str:
    try:
        call()
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected ValueError")
    assert expected_phrase in message, message
    return message


def test_env_key_preferred_over_file() -> None:
    with TemporaryDirectory() as tmp_dir:
        key_path = Path(tmp_dir) / "api_key.txt"
        key_path.write_text("file-key\n", encoding="utf-8")
        with patch.dict(os.environ, {"OPENAI_API_KEY": " env-key \n"}, clear=False):
            assert read_api_key(key_path) == "env-key"


def test_file_key_used_when_env_absent() -> None:
    with TemporaryDirectory() as tmp_dir:
        key_path = Path(tmp_dir) / "api_key.txt"
        key_path.write_text("file-key\n", encoding="utf-8")
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
            assert read_api_key(key_path) == "file-key"


def test_missing_key_message_is_portable() -> None:
    with TemporaryDirectory() as tmp_dir:
        missing_path = Path(tmp_dir) / "missing_key.txt"
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
            message = expect_value_error(lambda: read_api_key(missing_path), "Set OPENAI_API_KEY")
    assert "ignored local key file" in message
    for marker in legacy_local_markers():
        assert marker not in message, marker


def test_none_key_path_message_is_portable() -> None:
    with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
        message = expect_value_error(lambda: read_api_key(None), "Set OPENAI_API_KEY")
    assert "ignored local key file" in message
    for marker in legacy_local_markers():
        assert marker not in message, marker


def test_empty_file_rejected() -> None:
    with TemporaryDirectory() as tmp_dir:
        key_path = Path(tmp_dir) / "empty_key.txt"
        key_path.write_text(" \n", encoding="utf-8")
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
            message = expect_value_error(lambda: read_api_key(key_path), "API key file is empty")
    assert str(key_path) in message


def test_public_surfaces_do_not_hardcode_machine_key_paths() -> None:
    for rel_path in SURFACE_PATHS:
        text = rel_path.read_text(encoding="utf-8")
        for marker in legacy_local_markers():
            assert marker not in text, f"{rel_path} leaked legacy local API-key marker {marker!r}"


def main() -> None:
    test_env_key_preferred_over_file()
    test_file_key_used_when_env_absent()
    test_missing_key_message_is_portable()
    test_none_key_path_message_is_portable()
    test_empty_file_rejected()
    test_public_surfaces_do_not_hardcode_machine_key_paths()
    print("api-key loading tests passed")


if __name__ == "__main__":
    main()
