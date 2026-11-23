# CANO UGC ADS PRODUCTION STUDIO V1 — production handoff

## Scope
This draft-only commercial layer reuses `commercial_portfolio/campaigns.json` and the original portfolio generator, without replacing Product Intelligence, the Higgsfield adapter, Factory bridge, Kie plan-only PR, transcription or FFmpeg composition. It adds a six-scene reference-format preset and repeatable sales and ad-planning files for 3 fictional campaigns.

### Known resources / inventory
| Asset | Repository/branch | Status |
|---|---|---|
| Original UGC plans, verified claims gating, scope approval | `main` | Source code present; live E2E unverified |
| Higgsfield adapter | `main` | Code/guarded execution; provider auth and quality not verified in this environment |
| Factory production bridge | `main` | Contracts and integration code; no real media verified here |
| Kie.ai adapter | PR #10 | Plan-only, NOT a production source |
| MODULA/NUBA/LUMO commercial briefs | PR #11 (base of this branch) | Fictional, no masters |
| FFmpeg caption compositor | PR #12 | CI passed separately; not merged in this branch |
| Fail-closed Whisper/HyperFrames transcriber | PR #13 | CI passed separately; not merged in this branch |
| Creative Intelligence | `syacreator09-sys/creative-intelligence` | Schema/taxonomy and E6 brief PR #1; no external outcomes inferred |
| Santmun original `examples/anuncio-demo.mp4` | Public upstream reference | Binary listed, audiovisual content NOT inspected/compared |
| Original upstream avatar pool | Public upstream reference | No rights established; NOT imported |

### Santmun comparison
Upstream README/SKILL describe 6 scenes, ~30 seconds, 1080×1920, lip-sync, natural Latin American Spanish, HyperFrames captions, sequential provider jobs and optional Meta publish. Our independent parity preset provides *script/specification parity*, not video or performance parity. Source LICENSE file is missing in upstream main tree despite README stating MIT. Do not copy code, actors, logo, music or demo materials until rights/attribution confirmed.

## What this branch adds
All 3 campaigns use original Spanish copy, six beats (hook / problem / product / demonstration / benefit / CTA) at 5s each. Performance variants share all beats after scene 1; never infer which hook wins. The same source JSON exports a draft-only `script.json`, `storyboard.json`, `creative-brief.json`, `meta-ads-draft.json`, `qa-checklist.json`, bilingual `upwork-case.md`; plus `service-offers.json`.

```powershell
python scripts/build_commercial_portfolio.py --output .\storage\portfolio-briefs
python scripts/export_ugc_ads_drafts.py --output .\storage\ugc-ads-production-drafts
python -m pytest -q tests/test_commercial_portfolio.py tests/test_export_ugc_ads_drafts.py
```

## Publish/production gates
1. Replace fictional product with owned/licensed physical prop if actual product use is intended; verify product identity and rights.
2. Select an authorized avatar or owned talent. Do not use Santmun model pool or demo audio.
3. Use existing Product Intelligence and `UGCPlan` `scope_id`; human approves exact scope, cost, provider and budget *before* execution.
4. Pilot only ONE scene with approved provider after CLI auth and pricing confirmation.
5. On provider timeout, reconcile remote job state before any resubmit. Current Higgsfield implementation may re-submit ambiguous jobs and still needs hardened receipts/idempotency; do NOT launch full six-scene premium batch until fixed.
6. Visually inspect lipsync/skin/hands/packaging, dialogue and pronunciation, and document failures per scene.
7. Integrate PR #13 for fail-closed transcription and PR #12 for captioned technical composition, after careful branch reconciliation.
8. Confirm real `master.mp4` and six scene clips via FFprobe, render QA, rights and platform policy checks, then produce licensed thumbnails.
9. Only then change delivery status to `MASTER_VERIFIED`; do not claim creative performance metrics without measured evidence.

## Cost / commercial offer
Upwork cases provide service descriptions in EN/ES, offer scope and revisions without fictional rates. Provider credits and pricing are **NOT QUOTED** because real account configuration, selected model and rate have not been verified. Actual premium spend in this work: USD 0. Meta test proposals are not posted and have no spend.

## Compliance / Meta
Preview status is `NOT_PUBLISHED`; separate hook creative from shared body and CTA. Meta copy/claims/AI-disclosure fields are drafts for review against policies effective on publishing date. Do not launch or modify campaigns until explicit authorization.

## Desktop next action
Create a safe integration branch from this branch and bring in PR #12/#13, avoiding unrelated changes. Run all tests and FFmpeg/HyperFrames six-scene synthetic fixture; complete expensive-provider preflight only after all other gates pass.
