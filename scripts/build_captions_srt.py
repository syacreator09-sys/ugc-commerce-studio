#!/usr/bin/env python3
"""Build an auditable timed SRT from actual per-scene transcript JSON.

Offline and fail-closed: no generated/synthetic caption text, no provider calls.
Run after transcribe_correct.py and before composite_verified.py.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from scripts.composite_verified import inspect, scene_files

WORD_RE = re.compile(r"\s+")


def timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, rem = divmod(milliseconds, 3600000)
    minutes, rem = divmod(rem, 60000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def read_words(path: Path, duration: float) -> list[dict]:
    if not path.is_file() or not path.stat().st_size:
        raise ValueError(f"Missing or empty transcript: {path.name}")
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    words = raw.get("words") if isinstance(raw, dict) else raw
    if not isinstance(words, list) or not words:
        raise ValueError(f"Transcript has no word timings: {path.name}")
    validated = []
    previous_end = 0.0
    for index, word in enumerate(words, 1):
        if not isinstance(word, dict):
            raise ValueError(f"Invalid token {index} in {path.name}")
        text = word.get("text")
        start, end = word.get("start"), word.get("end")
        if not isinstance(text, str) or not text.strip() or not isinstance(start, (float, int)) or not isinstance(end, (float, int)):
            raise ValueError(f"Invalid token text/timing {index} in {path.name}")
        start, end = float(start), float(end)
        if not all(map(math.isfinite, (start, end))) or start < 0 or end <= start or start < previous_end - 0.025 or end > duration + 0.12:
            raise ValueError(f"Out-of-range or overlapping token {index} in {path.name}")
        validated.append({"text": WORD_RE.sub(" ", text.strip()), "start": start, "end": min(end, duration)})
        previous_end = end
    return validated


def build_srt(project: Path, output: Path | None = None, *, expected_scenes: int = 6,
              max_words: int = 5) -> dict:
    if not project.is_dir():
        raise ValueError(f"Scene directory not found: {project}")
    if expected_scenes < 1 or max_words < 1:
        raise ValueError("Expected scenes and max words must be positive")
    scenes = scene_files(project)
    if len(scenes) != expected_scenes:
        raise ValueError(f"Expected {expected_scenes} scene clips; found {len(scenes)}")
    output = output or project / "subtitles.srt"
    if output.resolve() in {s.resolve() for s in scenes}:
        raise ValueError("Refusing to overwrite an input clip")
    offsets = 0.0
    entries = []
    for number, scene in enumerate(scenes, 1):
        media = inspect(scene)
        duration = media["duration"]
        transcript = project / f"transcript-scene-{number}.json"
        words = read_words(transcript, duration)
        group = []
        for i, word in enumerate(words):
            group.append(word)
            if len(group) >= max_words or i == len(words) - 1 or re.search(r"[.!?]$", word["text"]):
                a = offsets + group[0]["start"]
                b = offsets + group[-1]["end"]
                if b - a < 0.07:
                    raise ValueError(f"Subtitle segment too short in scene {number}")
                entries.append((a, b, " ".join(item["text"] for item in group)))
                group = []
        offsets += duration
    for i in range(len(entries) - 1):
        if entries[i][1] > entries[i + 1][0]:
            raise ValueError("Subtitle groups overlap across scene boundaries")
    output.parent.mkdir(parents=True, exist_ok=True)
    serialized = "\n".join(
        f"{index}\n{timestamp(a)} --> {timestamp(b)}\n{text}\n"
        for index, (a, b, text) in enumerate(entries, 1)
    )
    output.write_text(serialized, encoding="utf-8")
    report = {
        "status": "TIMED_DRAFT_HUMAN_REVIEW_REQUIRED",
        "source": "actual_transcript_json",
        "scenes": expected_scenes,
        "segments": len(entries),
        "total_clip_duration_seconds": round(offsets, 3),
        "output": str(output),
        "human_approved": False,
    }
    (output.parent / "captions-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    p = argparse.ArgumentParser(description="Generate SRT from timecoded transcripts, no provider usage")
    p.add_argument("--project", required=True, type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--expected-scenes", type=int, default=6)
    p.add_argument("--max-words", type=int, default=5)
    args = p.parse_args()
    try:
        report = build_srt(args.project, args.output, expected_scenes=args.expected_scenes, max_words=args.max_words)
    except (ValueError, OSError, json.JSONDecodeError) as error:
        p.exit(2, f"SRT blocked: {error}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
