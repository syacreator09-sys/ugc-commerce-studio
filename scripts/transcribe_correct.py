#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--language", default="es")
    parser.add_argument("--model", default="small")
    args = parser.parse_args()

    scenes = sorted(args.project.glob("scene-*.mp4"))
    if not scenes:
        raise SystemExit("no scene-*.mp4 files found")

    for scene in scenes:
        result = subprocess.run(
            ["npx", "hyperframes", "transcribe", str(scene), "--model", args.model, "--language", args.language],
            cwd=args.project,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print(f"ERROR {scene.name}: {(result.stderr or result.stdout)[:300]}")
            continue
        source = args.project / "transcript.json"
        target = args.project / f"transcript-{scene.stem}.json"
        if source.exists():
            shutil.move(source, target)
            words = json.loads(target.read_text(encoding="utf-8"))
            print(f"OK {scene.name}: {len(words)} tokens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
