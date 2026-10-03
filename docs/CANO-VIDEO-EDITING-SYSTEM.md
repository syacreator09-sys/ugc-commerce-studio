# CANONICAL HOME MOVED

The canonical Cano video-editing system now lives in:

`syacreator09-sys/multimodal-content-engine`

Primary entrypoints:
- `templates/video-edit/TEMPLATE_REGISTRY_V1.json`
- `docs/video-engine/CANO_CHATGPT_WEB_EDITING_RUNTIME_V1.md`
- `templates/video-edit/CANO_UGC_SALES_V3_3.json`
- `templates/video-edit/cano-motion-ui-pack-v1/`

This file/repository copy is retained only as a migration backup. Do not treat it as the canonical editing source and do not evolve the render system here.

---

# CANO VIDEO EDITING SYSTEM — INDEX

Status: canonical reference index.

## Locked reference

`CANO_UGC_SALES_V3_3`

Existing files:
- `docs/CANO-UGC-SALES-MOTION-V3.md`
- `scripts/render_cano_ugc_sales_v3_clock.js`
- `scripts/render_cano_ugc_sales_v3_overlay.js`
- `scripts/render_cano_ugc_sales_v3_outro.js`

Rule: do not overwrite or redesign V3.3 without explicit Alfonso approval.

## Advanced motion family

`CANO_MOTION_UI_PACK_V1`

Path:
`scripts/motion/cano_motion_ui_pack_v1/`

Contains:
- `render_variations.js` — exact deterministic renderer for A–E.
- `assemble_all.sh` — FFmpeg composition.
- `qa_contact_sheets.sh` — technical + frame-sheet QA.
- `manifest.json` — timing, output names, rules and SHA-256 reference hashes.
- `package.json` — Node/Sharp dependency.
- `README.md` — operating instructions.

Families:
1. A_SOCIAL_CONVERSATION
2. B_COMMAND_CENTER
3. C_KINETIC_PHONE
4. D_FLOATING_APP_WORLD — face-safe corrected only
5. E_PROCESS_TRANSFORMATION

## Code stack actually used

`JavaScript -> SVG strings -> Sharp PNG sequence -> FFmpeg overlay/composition -> H.264 MP4 -> ffprobe/contact-sheet QA`

No After Effects dependency is required for these five styles.

## Storage rule

GitHub is the source of truth for reproducible code and design logic.
Large/private video source files and rendered MP4s are not committed to normal Git history.
Keep render outputs in media storage and verify against the SHA-256 values in the pack manifest.

## Core editing grammar

`spoken idea -> matching visual metaphor -> short motion/UI state -> next semantic beat -> reveal -> commercial CTA`

Motion must explain the narration, not merely decorate it.
