#!/usr/bin/env python3
"""Six 5-second synthetic media smoke: NO provider, NO products, NO real UGC.

This verifies the actual FFmpeg six-clip -> transcript SRT -> master data path
at low resolution to avoid wasting CI compute. It cannot validate real avatar,
lip-sync, rights, native 1080p quality or the Higgsfield CLI.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from scripts.build_captions_srt import build_srt
from scripts.composite_verified import compose

COLORS = ["0x202020", "0x383838", "0x505050", "0x686868", "0x808080", "0xa0a0a0"]


def smoke(output: Path) -> dict:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("FFmpeg and FFprobe required")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Smoke destination must be empty; never overwrite a production job")
    output.mkdir(parents=True, exist_ok=True)
    scenes = output / "scenes"
    scenes.mkdir()
    for i, color in enumerate(COLORS, 1):
        clip = scenes / f"scene-{i}.mp4"
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
            "-f", "lavfi", "-i", f"color=c={color}:s=180x320:r=12:d=5",
            "-f", "lavfi", "-i", f"sine=frequency={300 + i * 70}:sample_rate=48000:duration=5",
            "-t", "5", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "32",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "64k", "-shortest", str(clip),
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        transcript = [
            {"text": "Escena", "start": 0.2, "end": 0.8},
            {"text": str(i), "start": 0.8, "end": 1.25},
            {"text": "sintética.", "start": 1.25, "end": 1.95},
        ]
        (scenes / f"transcript-scene-{i}.json").write_text(
            json.dumps(transcript, ensure_ascii=False), encoding="utf-8"
        )
    captions = build_srt(scenes, expected_scenes=6)
    technical = compose(
        scenes, output / "synthetic-smoke-master.mp4",
        subtitles=scenes / "subtitles.srt",
        width=360, height=640, fps=12,
    )
    duration = technical["master"]["duration"]
    if not (29.2 <= duration <= 30.8):
        raise ValueError(f"Six-scene smoke duration failed: {duration}")
    if not technical["captions_burned"] or len(technical["scenes"]) != 6:
        raise ValueError("Six-scene smoke lacks expected media or captions")
    result = {
        "status": "SYNTHETIC_TECHNICAL_SMOKE_PASS",
        "scene_count": len(technical["scenes"]),
        "duration_seconds": duration,
        "dimensions": [360, 640],
        "captions": captions["segments"],
        "real_ugc_master": False,
        "human_qa": "NOT_PERFORMED",
        "premium_calls": 0,
    }
    (output / "smoke-result.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline FFmpeg/SRT 6x5s smoke at 360x640")
    parser.add_argument("--output", type=Path, help="Empty directory; default ephemeral temp")
    args = parser.parse_args()
    if args.output:
        result = smoke(args.output)
    else:
        with tempfile.TemporaryDirectory(prefix="cano-ugc-smoke-") as tmp:
            result = smoke(Path(tmp))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
