# AGENTS.md

## Mission

Convert verified owned or affiliate products into auditable UGC drafts using Higgsfield as the only premium generation engine.

## Required order

1. Read `README.md`, `SKILL.md`, `config/policies.json` and `config/higgsfield.json`.
2. Validate product rights, evidence, price, stock, commission and prohibited claims.
3. Build a plan and immutable `scope_id`.
4. Stop before premium generation.
5. Require an exact approval matching the scope.
6. Use the official Higgsfield CLI only.
7. Generate sequentially and save raw evidence.
8. Transcribe, caption, assemble and run human QA.
9. Export draft-only.

## Hard rules

- Higgsfield handles avatar, acting, voice, audio, lip-sync and generated UGC video.
- Do not connect HeyGen, Kie, ElevenLabs or LoRA in v1.
- Do not invent product claims, price, stock, commission or testimonials.
- Do not publish automatically.
- Do not commit secrets, private avatar media or customer assets.
- A failed scene is regenerated individually.

## Verification

```bash
python -m compileall -q src scripts
pytest -q
python scripts/doctor.py
```
