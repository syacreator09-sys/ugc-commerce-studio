# Workflow 04 — Product Intelligence

Use this workflow before requesting samples or spending Higgsfield credits on affiliate UGC.

## 1. Extract evidence

Accepted starting points:

- URL;
- JSON;
- copied offer/invitation text;
- screenshot interpreted by a multimodal agent;
- manual facts supplied by the operator.

The extraction layer reports what is visible/supplied. It does not calculate economics or fill missing facts.

## 2. Normalize

Convert evidence to `ProductOfferSnapshot`.

Every critical value carries:

```text
value
status = VERIFIED | INFERRED | ESTIMATED | UNKNOWN
source
verified_at (when available)
```

A visible value can be verified as **displayed evidence** without being verified as a different semantic field.

Example: `Earn $181.90` may be verified as `displayed_earnings_amount=181.90`, while currency and organic commission remain `UNKNOWN`.

## 3. Run deterministic economics

Organic and Shop Ads commission are independent.

```text
organic per sale = verified amount OR verified price × verified organic rate
Shop Ads per sale = verified amount OR verified price × verified Shop Ads rate
```

No verified price means no rate-based per-sale calculation.

Traffic projections require explicit scenario inputs:

```text
clicks = views × CTR
orders = views × CTR × CVR
commission = orders × commission_per_sale
```

CTR/CVR use decimals (`2% = 0.02`).

## 4. Run UGC fit

Use the existing legacy rubric without silently changing thresholds.

```text
raw score: 0..90
normalized score: raw / 90 × 100
```

If commission is unknown, use `commission_mxn=None`; commission points become zero rather than an invented value.

## 5. Assess confidence

Confidence penalizes missing/unverified:

- currency;
- price;
- organic commission;
- stock;
- demand;
- provenance;
- critical evidence contradictions.

High UGC fit plus low confidence is not a production green light.

## 6. Assess creative capacity

Count genuinely distinct hooks, audiences, use cases, demos, objections, transformations and formats.

Recommended initial batch:

```text
0 | 1 | 3 | 5 | 10+
```

`10+` requires a proven winner; it is not a first-test recommendation.

## 7. Apply hard gates

Before commercial scoring, reject if required by:

- medical/regulated claims necessary to sell the product;
- rejected rights;
- blocking platform restriction;
- critical evidence conflict.

Known non-blocking restrictions remain risk flags, not automatic hard rejects.

## 8. Emit two decisions

```text
sample_decision = SOLICITAR | NO_SOLICITAR | NEEDS_DATA
production_decision = PROCEDE | EN_ESPERA | RECHAZADO
```

A free sample can be `NEEDS_DATA` when economics or evidence quality is insufficient.

## 9. Operator gate

If Product Intelligence supports production, the operator still reviews:

- evidence;
- economics and assumptions;
- creative strategy;
- claims/risk;
- planned number of creatives.

Product Intelligence does not spend credits.

## 10. Production

Continue through existing flow:

```text
ProductManifest
→ plan
→ immutable scope_id
→ exact approval
→ Higgsfield
→ QA
→ draft-only
```

Affiliate copy must not invent personal use. Default to discovery/review language unless real experience is verified.

## 11. Measurement

Persist stable IDs for product, creative, hook, video and publication. Calculate:

```text
CTR
CVR
GMV
organic commission
Shop Ads commission
total commission
commission per view
commission per 1,000 views
commission per order
```

## 12. Learning and scale

Aggregate real results by channel/category/hook/format. Replace assumptions with own historical baselines as data accumulates.

```text
test small → measure → find winner → multiply winning angle
```
