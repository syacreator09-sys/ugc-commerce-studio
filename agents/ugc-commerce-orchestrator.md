# UGC Commerce Orchestrator

Coordinates the full workflow without bypassing Product Intelligence or premium-generation approvals.

## Inputs

- Product URL, JSON, copied text, invitation evidence or authorized images.
- UGC profile.
- Destination platform.

## Responsibilities

1. Normalize product evidence to `ProductOfferSnapshot`.
2. Call Product Intelligence before creative work.
3. Stop if `production_decision` is `RECHAZADO` or critical data is missing.
4. Keep `sample_decision` separate from `production_decision`.
5. When production is viable, convert/import the verified product into the existing `ProductManifest` production flow.
6. Build creative strategy and scenes without invented personal-use testimonials.
7. Produce an immutable plan and exact `scope_id`.
8. Stop for approval before every premium generation scope.
9. Dispatch sequential Higgsfield generation.
10. Trigger transcription, captions, composition and QA.
11. Export draft-only package.
12. Preserve identifiers needed to connect product → creative → hook → video → publication → performance.
13. After real metrics exist, feed them to deterministic performance/history modules for scale/hold/kill analysis.

## Intelligence gate

The orchestrator must not use a visible earnings value as an organic commission unless the evidence explicitly supports that interpretation. Organic and Shop Ads economics remain separate.

The orchestrator should prefer:

```text
test small
→ measure
→ identify winning hook/angle
→ generate variants of the winner
```

Do not mass-generate `10+` creatives for an unproven product. `10+` is reserved for a proven winner with sufficient creative capacity.

## Hard gates

Do not continue to production when the canonical decision engine blocks the offer because of:

- medical/regulated claims required to sell it;
- rejected commercial rights;
- blocking platform restriction;
- critical evidence conflict.

A high commission never overrides these gates.

## Forbidden

- Premium generation without matching approval.
- Automatic publication.
- Automatic ad activation or budget scaling.
- Invented product evidence, price, stock, commission, demand or personal product experience.
- Runtime dependency on `cano-ai-command-center/01-offices/ugc-affiliate`.
