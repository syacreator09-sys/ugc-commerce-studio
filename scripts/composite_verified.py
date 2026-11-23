#!/usr/bin/env python3
"""Fail-closed local UGC compositor; never uses providers or publishes."""
from __future__ import annotations
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

SCENE_RE = re.compile(r"scene-(\d+)\.mp4$")


def run(command):
    return subprocess.run(command, capture_output=True, text=True, check=True)


def inspect(path):
    payload = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]).stdout)
    video = next((s for s in payload.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = next((s for s in payload.get("streams", []) if s.get("codec_type") == "audio"), None)
    if video is None or audio is None:
        raise ValueError(f"Audio and video required: {path}")
    duration = float(payload["format"].get("duration", 0))
    if duration <= .1:
        raise ValueError(f"Invalid duration: {path}")
    return {"file": path.name, "duration": duration, "width": video["width"], "height": video["height"], "video_codec": video.get("codec_name"), "audio_codec": audio.get("codec_name")}


def scene_files(folder):
    candidates = []
    for path in folder.iterdir():
        match = SCENE_RE.fullmatch(path.name)
        if match:
            candidates.append((int(match.group(1)), path))
    candidates.sort()
    if not candidates or [n for n, _ in candidates] != list(range(1, len(candidates) + 1)):
        raise ValueError("Expected contiguous scene-1.mp4 ... scene-N.mp4")
    return [path for _, path in candidates]


def compose(folder, output, *, subtitles=None, width=1080, height=1920, fps=30):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg and ffprobe required")
    scenes = scene_files(folder)
    checks = [inspect(path) for path in scenes]
    if sum(x["duration"] for x in checks) > 120:
        raise ValueError("Duration exceeds safety limit")
    if subtitles is not None:
        subtitles = subtitles.resolve(strict=True)
        if not re.search(r"\d\d:\d\d:\d\d,\d{3}\s+-->\s+\d\d:\d\d:\d\d,\d{3}", subtitles.read_text(encoding="utf-8-sig")):
            raise ValueError("SRT has no valid timestamps")
    output = output.resolve()
    if output in [s.resolve() for s in scenes]:
        raise ValueError("Do not overwrite an input scene")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for path in scenes:
        command += ["-i", str(path)]
    filters = []
    references = []
    for i in range(len(scenes)):
        filters.append(f"[{i}:v:0]fps={fps},scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1,format=yuv420p,setpts=PTS-STARTPTS[v{i}]")
        filters.append(f"[{i}:a:0]aresample=async=1:first_pts=0,aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]")
        references.append(f"[v{i}][a{i}]")
    filters.append("".join(references) + f"concat=n={len(scenes)}:v=1:a=1[vcat][acat]")
    video_map = "[vcat]"
    if subtitles:
        # Keep the subtitle input local; escape reserved FFmpeg filter delimiters.
        esc = str(subtitles).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")
        filters.append(f"[vcat]subtitles=filename='{esc}':force_style='Alignment=2,MarginV=300,FontSize=18,Outline=2'[vout]")
        video_map = "[vout]"
    command += ["-filter_complex", ";".join(filters), "-map", video_map, "-map", "[acat]",
                "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac",
                "-b:a", "192k", "-movflags", "+faststart", str(output)]
    run(command)
    master = inspect(output)
    expected = sum(x["duration"] for x in checks)
    if master["width"] != width or master["height"] != height or abs(master["duration"] - expected) > max(.6, len(scenes) * .1):
        output.unlink(missing_ok=True)
        raise ValueError("Master failed technical checks")
    report = {"status": "TECHNICAL_PASS_VISUAL_REVIEW_PENDING", "master": master,
              "scenes": checks, "expected_duration": expected, "captions_burned": bool(subtitles),
              "human_qa": {"lip_sync": "NOT_VERIFIED", "avatar_continuity": "NOT_VERIFIED",
                           "product_identity": "NOT_VERIFIED", "pronunciation": "NOT_VERIFIED",
                           "commercial_claims": "NOT_VERIFIED"}, "auto_publish": False}
    (output.parent / "qa-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--subtitles", type=Path)
    parser.add_argument("--require-captions", action="store_true")
    args = parser.parse_args()
    if args.require_captions and not args.subtitles:
        parser.error("captions are required for this preset")
    print(json.dumps(compose(args.project, args.output or args.project / "master.mp4", subtitles=args.subtitles), indent=2))


if __name__ == "__main__":
    main()
