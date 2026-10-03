#!/usr/bin/env bash
set -euo pipefail

DIR="${1:-storage/output/cano_motion_ui_pack_v1}"
QA="${2:-storage/qa/cano_motion_ui_pack_v1}"
mkdir -p "$QA"

for f in "$DIR"/*.mp4; do
  [[ -e "$f" ]] || continue
  b=$(basename "$f" .mp4)
  ffprobe -v error \
    -show_entries format=duration \
    -show_entries stream=codec_name,width,height,r_frame_rate \
    -of default=nw=1 "$f" > "$QA/${b}_probe.txt"

  ffmpeg -y -loglevel error -i "$f" \
    -vf "fps=1,scale=270:-1,tile=5x4:padding=4:margin=4" \
    -frames:v 1 "$QA/${b}_sheet.jpg"
done

echo "QA written to $QA"
