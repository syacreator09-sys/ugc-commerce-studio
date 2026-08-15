# Claude Code instructions

When the user asks about a UGC product, TikTok Shop invitation, sample, affiliate opportunity or UGC production:

1. Read `SKILL.md` and `AGENTS.md`.
2. Run the setup workflow if `config/user-config.json` is missing.
3. Extract only visible/supplied product evidence. Never fill missing price, currency, commission, sales, stock or rules from guesswork.
4. Normalize to `ProductOfferSnapshot` and preserve evidence status (`VERIFIED`, `INFERRED`, `ESTIMATED`, `UNKNOWN`).
5. Use deterministic Product Intelligence before creative production:
   - `discover` to normalize already-extracted evidence;
   - `economics` for explicit CTR/CVR scenarios;
   - `scout` for the canonical Product Intelligence Report.
6. Treat organic commission and Shop Ads commission as separate values.
7. If an invitation shows `Earn $181.90` without an explicit currency, keep the amount as displayed evidence and the currency `UNKNOWN`.
8. Do not calculate a rate-based commission per sale without a verified price.
9. Respect hard gates and distinguish `sample_decision` from `production_decision`.
10. If production proceeds, import/validate the product and build the immutable plan.
11. Show the script and plan before spending credits.
12. Request approval for the exact `scope_id`.
13. Use `scripts/run_higgsfield_pilot.py` or the CLI for production.
14. Never publish, activate ads or scale budget automatically.
15. After publication data exists, use real CTR/CVR/orders/commission baselines instead of continuing to invent assumptions.

## Boundary

```text
LLM extracts evidence
→ deterministic Python calculates
→ LLM explains
→ human approves
→ Higgsfield produces
→ analytics learns
```

Do not invent personal product experience in affiliate UGC. Default copy should use discovery/review language such as `Me llamó la atención porque...`, not `Lo probé...`, unless real authorized experience is part of the evidence.

Higgsfield is the only premium provider. It generates the avatar/presenter, acting, voice, audio, lip-sync and video. FFmpeg/HyperFrames are post-production tools only.
