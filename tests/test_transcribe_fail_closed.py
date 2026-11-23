import importlib.util
import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("transcribe", ROOT / "scripts" / "transcribe_correct.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def scenes(tmp_path, count=2):
    for index in range(1, count + 1):
        (tmp_path / f"scene-{index}.mp4").write_bytes(b"placeholder")
    return tmp_path


def test_contiguous_scene_gate(tmp_path):
    (tmp_path / "scene-2.mp4").write_bytes(b"x")
    with pytest.raises(ValueError, match="contiguous"):
        mod.list_scenes(tmp_path)


def test_expected_scene_gate(tmp_path):
    scenes(tmp_path)
    with pytest.raises(ValueError, match="Expected 6"):
        mod.list_scenes(tmp_path, expected_scenes=6)


def test_empty_scene_rejected(tmp_path):
    (tmp_path / "scene-1.mp4").touch()
    with pytest.raises(ValueError, match="Empty"):
        mod.list_scenes(tmp_path)


def test_nonzero_exit_is_reported_and_fails(tmp_path):
    scenes(tmp_path, 1)
    with patch.object(mod.shutil, "which", return_value="/fake/npx"), patch.object(
        mod.subprocess, "run",
        return_value=subprocess.CompletedProcess([], 1, "", "offline failure"),
    ):
        report = mod.transcribe(tmp_path, expected_scenes=1)
    assert report["status"] == "FAILED"
    assert report["results"][0]["status"] == "FAILED"
    assert (tmp_path / "transcription-report.json").exists()


def test_stale_source_cannot_be_accepted(tmp_path):
    scenes(tmp_path, 1)
    (tmp_path / "transcript.json").write_text('[{"word":"stale"}]', encoding="utf-8")
    with patch.object(mod.shutil, "which", return_value="/fake/npx"), patch.object(
        mod.subprocess, "run",
        return_value=subprocess.CompletedProcess([], 0, "", ""),
    ):
        report = mod.transcribe(tmp_path, expected_scenes=1)
    assert report["status"] == "FAILED"
    assert not (tmp_path / "transcript-scene-1.json").exists()


def test_valid_transcript_is_saved(tmp_path):
    scenes(tmp_path, 1)
    def fake_run(*args, **kwargs):
        (tmp_path / "transcript.json").write_text(
            json.dumps([{"text": "hola", "start": 0.0, "end": 0.6}]), encoding="utf-8")
        return subprocess.CompletedProcess([], 0, "", "")
    with patch.object(mod.shutil, "which", return_value="/fake/npx"), patch.object(
        mod.subprocess, "run", side_effect=fake_run
    ):
        report = mod.transcribe(tmp_path, expected_scenes=1)
    assert report["status"] == "PASS"
    assert (tmp_path / "transcript-scene-1.json").exists()


def test_failed_scene_invalidates_prior_target(tmp_path):
    scenes(tmp_path, 1)
    (tmp_path / "transcript-scene-1.json").write_text('["old"]', encoding="utf-8")
    with patch.object(mod.shutil, "which", return_value="/fake/npx"), patch.object(
        mod.subprocess, "run",
        return_value=subprocess.CompletedProcess([], 1, "", "error"),
    ):
        report = mod.transcribe(tmp_path, expected_scenes=1)
    assert report["status"] == "FAILED"
    assert not (tmp_path / "transcript-scene-1.json").exists()
