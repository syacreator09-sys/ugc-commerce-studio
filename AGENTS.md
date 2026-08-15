# AGENTS.md

## Mission

Convert verified owned or affiliate opportunities into auditable UGC decisions and drafts, using deterministic Product Intelligence before Higgsfield premium generation.

## Required order

1. Read `README.md`, `SKILL.md`, `config/policies.json` and `config/higgsfield.json`.
2. Extract product evidence from URL/JSON/text/capture without inventing missing values.
3. Normalize commercial evidence to `ProductOfferSnapshot` with `VERIFIED | INFERRED | ESTIMATED | UNKNOWN` status.
4. Validate product rights, evidence, price, currency, stock, organic commission, Shop Ads commission, demand and prohibited claims.
5. Run Product Intelligence: economics, UGC fit, confidence, creative capacity and hard gates.
6. Emit `sample_decision` and `production_decision` separately.
7. If production can proceed, build a plan and immutable `scope_id`.
8. Stop before premium generation.
9. Require an exact approval matching the scope.
10. Use the official Higgsfield CLI only.
11. Generate sequentially and save raw evidence.
12. Transcribe, caption, assemble and run human QA.
13. Export draft-only.
14. Record real performance so historical baselines can replace assumptions over time.

## Hard rules

- Higgsfield handles avatar, acting, voice, audio, lip-sync and generated UGC video.
- Do not connect HeyGen, Kie, ElevenLabs or LoRA in v1.
- Do not invent product claims, price, currency, stock, commission, demand, testimonials or personal product use.
- `Earn X` is a displayed value only until its meaning and currency are verified.
- Organic commission and Shop Ads commission are independent fields and calculations.
- If price is unknown, do not calculate a rate-based commission per sale.
- If commission is unknown, UGC scoring may assign zero commission points conservatively; never fabricate a commission value.
- Hard gates execute before commercial scoring. High commission cannot override medical/regulated claims, rejected rights, a blocking platform restriction or critical evidence conflict.
- Product Intelligence commands must not trigger premium generation.
- Do not publish automatically.
- Do not activate ads or scale budget automatically.
- Do not commit secrets, private avatar media or customer assets.
- A failed scene is regenerated individually.
- `cano-ai-command-center/01-offices/ugc-affiliate` is reference/control only; do not create a runtime dependency back to it.

## Canonical calculation boundary

```text
LLM/provider extracts evidence
→ deterministic Python validates/calculates
→ agent explains the report
→ human approves exact scope
→ Higgsfield produces
→ analytics closes the feedback loop
```

## Verification

```bash
python -m compileall -q src scripts
pytest -q
python scripts/doctor.py
```
