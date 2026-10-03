# Google Flow Product Audit — 2026-10-03

## Status
Source: Gemini direct audit supplied by user.
Canonicalization policy: official Google Flow/Labs documentation overrides Gemini-provided claims. Unsupported details remain UNVERIFIED.

## Officially verified in this review
### Flow Agent
- Web/PC.
- Brainstorming and planning.
- Generates images/videos and selects an appropriate model.
- Directly edits selected project media.
- Batch variations.
- Organizes assets: rename, collections, archive unused assets.
- Generated media is saved to the active project.
- Agent queries currently cost zero Flow credits but have a daily query quota.
- Media generations consume Flow credits.

### Flow Tools
- Custom reusable Tools/mini-apps can be created from natural-language requirements.
- Flow writes code and builds the Tool interface.
- Tools can be edited conversationally.
- Tools can be pinned, added to the library, remixed and shared.
- Shared links expose the Tool code, name and thumbnail.
- Media generated through Tools consumes Flow credits and is saved to the active project.
- Google displays a warning banner when running a Tool may consume credits.
- Tool creation has a daily quota.

### Video editing / Scene Builder
- Uploaded and generated videos can be edited.
- Previous edit versions/prompts are retained in History/Stacks.
- Multiple videos can be selected for batch editing on desktop.
- Veo-generated clips can be extended subject to model compatibility.
- A video frame can be saved as an image and reused as Ingredient, Start Frame or End Frame.
- Scene Builder can arrange clips, reorder, trim, preview and download a scene.
- Advanced Scene Builder/camera/batch editing features are desktop-only.

### Model compatibility
Canonical compatibility remains in CURRENT_STATE.json and follows the current Flow models/features help page.

## Gemini claims retained as UNVERIFIED, not canonical
- Tools arbitrary multi-step model pipelines.
- Tools IF/ELSE semantics.
- Tools batch-N semantics.
- Tools explicit model-by-model selector access.
- Tools direct Omni/Veo/Lyria routing.
- Tools inability to loop or retry.
- Tools computer-vision scoring limitations.
- Agent automatic image -> First Frame -> video -> Extend chaining without operator intervention.
- Agent inability to visually compare/evaluate generated outputs.
- Agent direct music generation via Lyria.
- Agent asset deletion (official help reviewed says archive unused assets, not delete).
- Scene Builder audio/music-track capabilities, crossfades, transitions, split emulation and audio gain behavior.
- Exact upload/export codec and file-size claims.
- 720p->1080p/4K upscale pipeline details and claimed temporal latent super-resolution implementation.
- Exact failure/refund behavior.
- Claimed practical 50-video/day Flow UI boundary.
- Claimed 2–4 parallel backend render concurrency.
- Claimed absence of project recycle bin/duplicate/collaboration features unless separately verified.

## Production consequence
Flow is now treated as a verified interactive production/orchestration surface, but not as a fully autonomous headless workflow engine. Our own automation stack remains responsible for deterministic QA, conditional retries, budgets, large-scale orchestration and final programmatic assembly until Flow documents/tests prove otherwise.

## Official sources
- https://support.google.com/flow/answer/17093911
- https://support.google.com/flow/answer/17104535
- https://support.google.com/labs/answer/16935718
- https://support.google.com/flow/answer/16352836
