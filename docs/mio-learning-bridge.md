# MIO learning bridge

`ugc-commerce-studio` remains the authority for product evidence, affiliate economics, cost/benefit, production approval and immutable scope. Media Intelligence Office (MIO) may provide two inputs only:

1. evidence-backed first-party CTR/CVR priors;
2. creative experiment trace such as brief, experiment, variant, hook family, story arc and evidence references.

## Prior rules

- explicit operator scenarios always override a historical prior;
- prior platform must match the product platform (`tiktok_shop` normalizes to `tiktok`);
- prior must be `WIN` or `PROMISING`, meet the configured sample-size threshold and confidence threshold, and contain decimal CTR/CVR rates;
- `INCONCLUSIVE`, mismatched or incomplete priors are not silently used;
- prior-derived conservative/aggressive scenarios are estimates, not facts;
- organic and Shop Ads commissions remain separate.

## Review evidence rules

`CommerceReviewEvidenceV1` is market/creative evidence only. Recurring complaints, unmet needs and quality expectations may become angle candidates, but they must never be promoted into `verified_benefits` or product claims without independent verification.

## Immutable creative trace

When MIO trace fields are supplied to `build_factory_order`, they are part of the SHA-256 approval scope. Changing a variant, hook, brief, experiment, narrative, series, visual style, CTA, pacing or evidence references produces a different scope/order ID and therefore requires a new human approval.

Pre-extension v1 orders that omitted these optional fields remain verifiable with their original scope.
