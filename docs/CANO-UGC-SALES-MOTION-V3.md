# CANO UGC Sales Motion V3

Canonical post-production pattern for a **UGC → proof/reveal → commercial CTA** edit.

Status: **CANONICAL / APPROVED — V3.3**
Owner: Cano Digital.
Runtime: HTML/SVG-like motion rendered with Node + Sharp, assembled with FFmpeg.
Do not publish automatically.

> Canonical rule: preserve this motion language as the reference for future Cano UGC sales edits. Do not redesign or replace it unless Alfonso explicitly asks for a new visual system.

## Why this version exists

The working pattern keeps the UGC human and believable first, then adds motion only where it reinforces the spoken idea. It avoids turning the whole video into a dashboard.

Sequence:

1. UGC hook remains visually clean.
2. A small contextual motion card reinforces a high-value spoken phrase.
3. Task-flow overlays appear only during matching narration.
4. The reveal ("Todo esto es IA") lands before the sales layer.
5. Final frame becomes a premium dark-glass Cano Digital sales interface.
6. CTA is concrete: **MÁNDAME TU PRODUCTO**.

## Approved visual language

- 1080×1920, 24 fps.
- Dark glass panels.
- White typography.
- Gold accent: #FFBF3B.
- Electric blue accent: #56B7FF.
- Rounded cards; restrained glow.
- UI appears in layers, not all at once.
- Preserve face, product and burned captions.
- No fabricated performance metrics.
- Motion should explain the narration, not decorate it.
- Prefer one visual metaphor per spoken idea.
- Keep overlays short, contextual and subordinate to the UGC performance.

## V3.3 motion map

### 0.05–3.02 s — time-saving clock
Narration: "Esto me ahorra dos horas al día."

Overlay:
- label: AHORRO DE TIEMPO
- digital counter animates 0:00 → 2:00
- circular clock/progress ring
- final micro-badge: 2 H / DÍA

This layer only visualizes the spoken claim. Do not add percentages or unsupported performance claims.

### 4.45–11.85 s — AI TASK FLOW
- CAPTURANDO PENDIENTES
- ARMANDO TU DÍA
- PRIORIZANDO TAREAS
- SOLO LO IMPORTANTE

Each state has a matching microvisual: waveform, plan progress, priority bars, focus target.

### Final reveal / sales outro
Keep the reveal first. Then freeze/clean the final UGC frame and animate:
- AI CREATIVE // LIVE
- 1 PRODUCTO → 4 FORMATOS
- IMAGINA ESTO / CON TU PRODUCTO.
- AI UGC / REELS / ADS / CREATIVOS
- TU PRODUCTO. TU MARCA.
- Nosotros creamos el anuncio.
- MÁNDAME TU PRODUCTO
- Te digo qué anuncio haría para tu marca.
- Creative pipeline progress.

## Files

- scripts/render_cano_ugc_sales_v3_clock.js
- scripts/render_cano_ugc_sales_v3_overlay.js
- scripts/render_cano_ugc_sales_v3_outro.js

These scripts generate transparent PNG sequences (clock/task flow) or full outro frames. Source UGC/customer media is intentionally not committed.

## Example assembly

Clock layer over an already approved master:

```bash
node scripts/render_cano_ugc_sales_v3_clock.js

ffmpeg -i approved-master.mp4 \
  -framerate 24 -i storage/render/cano_ugc_v3_clock_frames/frame_%04d.png \
  -filter_complex "[0:v][1:v]overlay=0:0:eof_action=pass:format=auto[v]" \
  -map "[v]" -map 0:a? \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
  -c:a copy -movflags +faststart output-v3-3.mp4
```

For the final outro, set `CANO_OUTRO_BASE` to the cleaned final UGC frame before running the outro renderer.

## Reuse rule

Do not copy this layout mechanically to every channel. Reuse the **motion grammar**:

spoken concept → one visual metaphor → short UI state → clear CTA.

For Cano Digital, this premium tech treatment is native. Other channels need channel-specific art direction.

## Locked reference

The approved reference version is **CANO_UGC_SALES_V3_3**.

When building future Cano UGC edits:
- start from this motion grammar;
- preserve the same hierarchy and restraint;
- change only the metaphor, copy and CTA required by the new script;
- never add decorative dashboards that do not match the spoken idea;
- never overwrite this canonical reference without explicit approval.
