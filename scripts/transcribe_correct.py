#!/usr/bin/env python3
"""Transcribe actual scene media, fail closed, with per-scene execution evidence.

This script never invokes a paid generator. All missing/failed transcripts abort
the job and return nonzero. No invented captions or synthetic fallback.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCENE_RE = re.compile(r"scene-(\d+)\.mp4$")


def list_scenes(project: Path, expected_scenes: int | None = None) -> list[Path]:
    matches = []
    for path in project.iterdir():
        match = SCENE_RE.fullmatch(path.name)
        if match:
            matches.append((int(match.group(1)), path))
    matches.sort(key=lambda item: item[0])
    numbers = [n for n, _ in matches]
    if not numbers or numbers != list(range(1, len(numbers) + 1)):
        raise ValueError("Scene filenames must be contiguous: scene-1.mp4 ... scene-N.mp4")
    if expected_scenes is not None and len(matches) != expected_scenes:
        raise ValueError(f"Expected {expected_scenes} scenes, found {len(matches)}")
    for _, scene in matches:
        if scene.stat().st_size == 0:
            raise ValueError(f"Empty scene file: {scene.name}")
    return [scene for _, scene in matches]


def transcribe(project: Path, *, language: str = "es", model: str = "small",
               expected_scenes: int | None = None) -> dict:
    if not shutil.which("npx"):
        raise RuntimeError("npx is required for HyperFrames transcription")
    scenes = list_scenes(project, expected_scenes)
    results = []
    failed = False
    for scene in scenes:
        source = project / "transcript.json"
        target = project / f"transcript-{scene.stem}.json"
        # Prevent an output from a prior scene/job being mistaken for a fresh transcript.
        source.unlink(missing_ok=True)
        record = {"scene": scene.name, "status": "FAILED", "transcript": None}
        try:
            completed = subprocess.run(
                ["npx", "--no-install", "hyperframes", "transcribe", str(scene.resolve()),
                 "--model", model, "--language", language],
                cwd=project, capture_output=True, text=True, timeout=900, check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(f"HyperFrames exit {completed.returncode}: {(completed.stderr or completed.stdout)[:200]}")
            if not source.is_file() or source.stat().st_size == 0:
                raise RuntimeError("HyperFrames did not produce transcript.json")
            transcript = json.loads(source.read_text(encoding="utf-8"))
            if not isinstance(transcript, (list, dict)) or not transcript:
                raise ValueError("Transcript is empty or has invalid structure")
            source.replace(target)
            record.update({"status": "PASS", "transcript": target.name})
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as error:
            source.unlink(missing_ok=True)
            target.unlink(missing_ok=True)
            record["error"] = str(error)[:400]
            failed = True
        results.append(record)
    report = {"status": "FAILED" if failed else "PASS", "expected_scenes": expected_scenes,
              "actual_scenes": len(scenes), "results": results}
    (project / "transcription-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcribe all scenes, failing if any fails")
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--language", default="es")
    parser.add_argument("--model", default="small")
    parser.add_argument("--expected-scenes", type=int, default=None)
    args = parser.parse_args()
    if not args.project.is_dir():
        parser.error("--project must be an existing directory")
    if args.expected_scenes is not None and args.expected_scenes < 1:
        parser.error("--expected-scenes must be positive")
    try:
        report = transcribe(args.project, language=args.language, model=args.model,
                            expected_scenes=args.expected_scenes)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"TRANSCRIPTION BLOCKED: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
