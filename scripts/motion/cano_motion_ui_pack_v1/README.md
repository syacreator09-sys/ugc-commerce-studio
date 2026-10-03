# CANO MOTION UI PACK V1

Reusable post-production pack for Cano Digital UGC / talking-head videos.

This pack is **separate from and must not replace** the locked reference `CANO_UGC_SALES_V3_3`.

## What is preserved

Five complete visual families:

- `A_SOCIAL_CONVERSATION` — conversation bubbles, tasks, calendar, priorities.
- `B_COMMAND_CENTER` — SaaS control center, agenda, priority engine, focus mode.
- `C_KINETIC_PHONE` — kinetic type, large semantic words, phone/app UI.
- `D_FLOATING_APP_WORLD` — floating interface cards around the presenter. **Face-safe corrected version only.**
- `E_PROCESS_TRANSFORMATION` — visual chaos transformed into an organized AI pipeline.

All five share the same visual grammar:

`spoken phrase -> visual metaphor -> motion state -> reveal -> CTA`

## Runtime used

- JavaScript / Node.js
- SVG generated as strings
- `sharp` to rasterize transparent PNG sequences
- FFmpeg to composite the PNG sequence over the approved video master
- ffprobe + FFmpeg contact sheets for QA

This is the same deterministic code-first approach used in the approved experiments. It does not require After Effects.

## Install

```bash
cd scripts/motion/cano_motion_ui_pack_v1
npm install
```

Requirements available on PATH:

```text
node
ffmpeg
ffprobe
```

## Render all overlay families

```bash
npm run render
```

Default frame output:

```text
storage/render/cano_motion_ui_pack_v1/
  A_SOCIAL_CONVERSATION/
  B_COMMAND_CENTER/
  C_KINETIC_PHONE/
  D_FLOATING_APP_WORLD/
  E_PROCESS_TRANSFORMATION/
```

You can render selected families:

```bash
node render_variations.js A_SOCIAL_CONVERSATION C_KINETIC_PHONE
```

## Assemble on an approved master

```bash
./assemble_all.sh /path/to/approved_master.mp4
```

Final output defaults to:

```text
storage/output/cano_motion_ui_pack_v1/
```

The approved test used a 1080x1920 / 24fps / ~19.55s base master. The generated overlays are rendered at 12fps and normalized to 24fps during FFmpeg composition.

## QA

```bash
./qa_contact_sheets.sh storage/output/cano_motion_ui_pack_v1
```

This writes ffprobe metadata plus 1fps contact sheets. Visual QA is mandatory: a technically valid render can still cover a face or collide with captions.

## Protected reference

`CANO_UGC_SALES_V3_3` stays locked. Its own renderer remains under the existing V3 files in the repository.

Do not mutate V3.3 to create these variants. Build from this pack instead.

## Storage policy

Git stores:

- renderer source;
- timing;
- copy;
- colors;
- assembly commands;
- QA process;
- manifest + checksums.

Git does **not** store:

- customer/source UGC;
- private avatar media;
- final large MP4 outputs.

Final renders belong in Drive / Cloudinary / R2 or another media store. `manifest.json` contains SHA-256 hashes of the approved reference outputs so a later copy can be verified byte-for-byte.

## Canonical visual rules

1. Motion explains the spoken phrase; it is not decorative.
2. Do not cover eyes, mouth, hero product or important burned captions.
3. One visual metaphor per semantic beat.
4. UI can be dense only when the narration supports it.
5. No fabricated sales/conversion/view metrics.
6. Reveal lands before commercial CTA.
7. CTA stays concrete: product/brand/action, not generic “learn more”.
8. Family D must use the corrected face-safe composition.
