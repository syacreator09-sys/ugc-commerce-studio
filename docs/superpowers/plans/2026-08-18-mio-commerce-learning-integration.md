# MIO ↔ Commerce ↔ Factory Learning Integration Plan

**Date:** 2026-08-18

## Goal

Extend the existing UGC Commerce → Factory bridge without changing its authority boundaries:

- `ugc-commerce-studio` remains the source of truth for product evidence, affiliate economics, cost/benefit, approval and immutable production scope.
- `media-intelligence-office.` remains the source of truth for creative strategy, experiments and evidence-backed creative learning.
- `factory-ia-channel-v5` remains the production/runtime authority and chooses render implementations.
- `product-ip-factory` may export normalized review evidence only; review language never becomes a verified product claim.
- `cano-hybrid-composer-skill` may be invoked only behind Factory as an optional explicitly-authorized compositor if its current contract adds value. Commerce and MIO never call it directly.
- `adaptive-agent-harness` is a build/verification methodology, not a business runtime dependency.

## Invariants

1. No automatic publication, ad activation, budget scaling or premium spend.
2. Human approval remains bound to the exact SHA-256 commerce production scope.
3. Organic affiliate commission and Shop Ads commission remain separate.
4. Historical priors never override explicit operator assumptions.
5. Priors are comparable only within the same platform and observation window.
6. Small or weak samples are `INCONCLUSIVE` and cannot silently become base assumptions.
7. CTR/CVR are decimal rates (`0.02` = 2%).
8. Review evidence is angle/problem evidence, not `verified_benefits` or product claims.
9. MIO does not select Higgsfield, LTX, H3, FFmpeg, Remotion or another render engine.
10. Factory may not expand a creative scope after approval.
11. Cross-system IDs must remain traceable from strategy to order to production to performance.

## Contracts

### 1. `CommercePerformancePriorV1`

MIO exports an evidence-backed first-party prior with:

- `schema_version`, `prior_id`, `platform`, `window_hours`, `filters`, `sample_size`
- `ctr_median`, `cvr_median`, dispersion fields
- `classification`: `WIN | PROMISING | INCONCLUSIVE | LOSE`
- `confidence_score`, `source_refs`, `generated_at`

Rules: mixed platform/window rows are rejected or partitioned before export; median is deterministic; sample-size policy is explicit; no causal claim is emitted.

### 2. Commerce creative trace

Extend `CommerceProductionOrderV1` with optional `mio_brief_id`, `experiment_id`, `variant_id`, `narrative_id`, `series_id`, `hook_family`, `story_arc`, `visual_style`, `cta_style`, `pacing`, and `evidence_refs`. These fields participate in the immutable scope.

### 3. `CommerceReviewEvidenceV1`

Product IP Factory exports a compact review-evidence contract with product/listing reference, sample/rating summary, positive/negative themes, recurring complaints, unmet needs, quality expectations, source refs/provenance and timestamp. It must not contain verified-claim semantics or full raw review bodies.

Commerce imports review evidence into creative angle candidates and provenance only.

### 4. Cross-system trace

Preserve when available: `content_id → brief_id → experiment_id → variant_id → product_id → order_id → scope_id → idea_id → job_id → creative_id/video_id → performance snapshot`.

## Workstreams

### A. MIO
1. Add schema/model/exporter for `CommercePerformancePriorV1`.
2. Compute deterministic medians/dispersion from comparable first-party rows.
3. Enforce same platform + window and small-sample `INCONCLUSIVE` behavior.
4. Extend UGC production brief with optional commerce context/creative trace without renderer/model fields.
5. Add CLI/export path and tests.

### B. UGC Commerce Studio
1. Add local mirror/model for MIO performance prior.
2. Add prior application for production economics: explicit assumptions win; compatible strong priors may fill missing base CTR/CVR; weak/inconclusive priors are ignored.
3. Add review-evidence model/importer; only angle candidates/provenance may be derived.
4. Extend `CommerceProductionOrderV1` and schema with creative trace fields.
5. Ensure creative-trace mutation changes SHA scope/order ID.
6. Add tests/CLI surface.

### C. Product IP Factory
1. Add stable exporter from deterministic `ReviewDigest` to `CommerceReviewEvidenceV1`.
2. Preserve source references/provenance.
3. No raw-review or verified-claim semantics.
4. Add pure function/CLI surface and tests.

### D. Factory V5
1. Mirror additive Commerce order fields.
2. Persist MIO/experiment/variant trace into Idea metadata and job manifest.
3. Preserve approval scope and all publication/premium gates.
4. Audit Hybrid Composer; integrate only if additive, opt-in and dry-run-safe.
5. Add tests.

### E. Hybrid Composer
Audit first. Modify only if Factory needs a stable machine-readable adapter. Do not add GitHub Actions contrary to current repository policy and never activate live rendering implicitly.

## TDD acceptance cases

MIO: compatible rows produce deterministic medians; mixed platform/window fails; small sample is `INCONCLUSIVE`; UGC brief accepts commerce context; no renderer/model field.

Commerce: compatible prior can fill missing base CTR/CVR; inconclusive prior ignored; explicit assumptions override prior; creative trace changes scope; review evidence never populates verified benefits; angle candidates/provenance preserved; schema validates.

Product IP: ReviewDigest export deterministic; no raw review bodies; no verified-claim semantics; source refs retained.

Factory: MIO IDs reach Idea/job trace; existing scope/idempotency remain; no publication side effect; Hybrid route if implemented is opt-in and dry-run-safe.

## Verification gates

For every modified repo: record baseline where possible, add contract tests before implementation where practical, run compile/type/build + full tests + doctor/validation, require green PR CI before merge, then verify `main` post-merge.

## Non-goals

No `video-lora-lab` integration until it has an auditable runtime. No second creative brain via `cano-adaptive-content-skill`. No new repo. No marketplace/publication bypass. No rename-by-copy of `media-intelligence-office.`; repo rename remains an owner/admin action if tooling cannot perform it.
