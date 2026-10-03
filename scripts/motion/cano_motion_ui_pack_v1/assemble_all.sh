#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-}"
FRAME_ROOT="${CANO_MOTION_OUT:-storage/render/cano_motion_ui_pack_v1}"
OUT_DIR="${2:-storage/output/cano_motion_ui_pack_v1}"
FPS="${CANO_OUTPUT_FPS:-24}"
CRF="${CANO_OUTPUT_CRF:-18}"
PRESET="${CANO_OUTPUT_PRESET:-medium}"

if [[ -z "$BASE" || ! -f "$BASE" ]]; then
  echo "Usage: $0 /path/to/base_master.mp4 [output_dir]" >&2
  exit 2
fi
mkdir -p "$OUT_DIR"

assemble() {
  local family="$1" out="$2"
  local frames="$FRAME_ROOT/$family/frame_%04d.png"
  ffmpeg -y -loglevel error \
    -i "$BASE" \
    -framerate 12 -i "$frames" \
    -filter_complex "[1:v]fps=${FPS}[ov];[0:v][ov]overlay=0:0:format=auto:eof_action=pass[v]" \
    -map "[v]" -map 0:a? \
    -c:v libx264 -crf "$CRF" -preset "$PRESET" -pix_fmt yuv420p \
    -c:a copy -movflags +faststart -shortest "$out"
}

assemble A_SOCIAL_CONVERSATION "$OUT_DIR/CANO_A_SOCIAL_CONVERSATION_FULL.mp4"
assemble B_COMMAND_CENTER "$OUT_DIR/CANO_B_COMMAND_CENTER_FULL.mp4"
assemble C_KINETIC_PHONE "$OUT_DIR/CANO_C_KINETIC_PHONE_FULL.mp4"
assemble D_FLOATING_APP_WORLD "$OUT_DIR/CANO_D_FLOATING_APP_WORLD_FULL_FIXED_FINAL.mp4"
assemble E_PROCESS_TRANSFORMATION "$OUT_DIR/CANO_E_PROCESS_TRANSFORMATION_FULL.mp4"

echo "Rendered outputs in $OUT_DIR"
