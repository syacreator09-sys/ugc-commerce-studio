"""Fail-closed SRT conversion tests. No premium calls."""
import json
import pytest
from scripts import build_captions_srt as captions


def fixture_project(tmp_path, count=6):
    for i in range(1, count + 1):
        (tmp_path / f"scene-{i}.mp4").write_bytes(b"x")
        (tmp_path / f"transcript-scene-{i}.json").write_text(
            json.dumps([
                {"text": "Hola", "start": 0.0, "end": 0.4},
                {"text": "mundo.", "start": 0.4, "end": 0.8},
            ]), encoding="utf-8"
        )
    return tmp_path


def test_srt_uses_media_offsets_and_real_words(monkeypatch, tmp_path):
    project = fixture_project(tmp_path)
    monkeypatch.setattr(captions, "inspect", lambda clip: {"duration": 5.0})
    report = captions.build_srt(project, expected_scenes=6)
    data = (project / "subtitles.srt").read_text(encoding="utf-8")
    assert report["status"] == "TIMED_DRAFT_HUMAN_REVIEW_REQUIRED"
    assert report["segments"] == 6
    assert "00:00:00,000 --> 00:00:00,800" in data
    assert "00:00:25,000 --> 00:00:25,800" in data
    assert data.count("Hola mundo.") == 6
    assert (project / "captions-report.json").exists()


def test_missing_transcript_blocks_delivery(monkeypatch, tmp_path):
    project = fixture_project(tmp_path)
    (project / "transcript-scene-4.json").unlink()
    monkeypatch.setattr(captions, "inspect", lambda clip: {"duration": 5.0})
    with pytest.raises(ValueError, match="Missing or empty"):
        captions.build_srt(project)
    assert not (project / "subtitles.srt").exists()


def test_overlap_and_out_of_range_block(monkeypatch, tmp_path):
    project = fixture_project(tmp_path, count=1)
    monkeypatch.setattr(captions, "inspect", lambda clip: {"duration": 5.0})
    transcript = project / "transcript-scene-1.json"
    transcript.write_text(json.dumps([
        {"text": "A", "start": 0, "end": 2},
        {"text": "B", "start": 1, "end": 3}
    ]), encoding="utf-8")
    with pytest.raises(ValueError, match="overlapping"):
        captions.build_srt(project, expected_scenes=1)
    transcript.write_text(json.dumps([
        {"text": "A", "start": 4.9, "end": 5.3}
    ]), encoding="utf-8")
    with pytest.raises(ValueError, match="Out-of-range"):
        captions.build_srt(project, expected_scenes=1)


def test_rejects_non_tokenized_fake_text(monkeypatch, tmp_path):
    project = fixture_project(tmp_path, count=1)
    monkeypatch.setattr(captions, "inspect", lambda clip: {"duration": 5.0})
    (project / "transcript-scene-1.json").write_text(
        json.dumps({"text": "guion sin audio"}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="no word timings"):
        captions.build_srt(project, expected_scenes=1)
