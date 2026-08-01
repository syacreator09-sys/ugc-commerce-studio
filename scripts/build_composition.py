#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    scenes = sorted(args.project.glob("scene-*.mp4"))
    if not scenes:
        raise SystemExit("no scene-*.mp4 files found")

    output = args.output or args.project / "master.mp4"
    concat = args.project / "concat.txt"
    concat.write_text("\n".join(f"file '{scene.resolve()}'" for scene in scenes), encoding="utf-8")

    command = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
        "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart", str(output),
    ]
    subprocess.run(command, check=True)
    report = {
        "output": str(output),
        "scenes": [str(scene) for scene in scenes],
        "scene_durations": [duration(scene) for scene in scenes],
        "total_duration": duration(output),
        "auto_publish": False,
    }
    (args.project / "composition-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
