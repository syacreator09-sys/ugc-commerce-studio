# Cost/Benefit → Factory UGC Production Bridge

`ugc-commerce-studio` is the economic decision boundary. `factory-ia-channel-v5` is the production boundary. The repositories do not import each other at runtime; they exchange versioned JSON.

## Decision flow

```text
ProductOfferSnapshot
→ Product Intelligence
→ Production cost inputs
→ conservative / base / aggressive economics
→ NEEDS_DATA | NOT_ECONOMIC | APPROVAL_REQUIRED
→ immutable CommerceProductionOrderV1
→ explicit human approval
→ Factory V5 ingest
→ one UGC ProductionJob per approved angle
→ FactoryProductionReceiptV1
→ real performance returns to Commerce history
```

`APPROVAL_REQUIRED` means the base scenario covers the explicit test cost. It is never an automatic approval and it is never a promise of profit.

Shop Ads commission remains a separate projection. It is **not** added to organic commission when deciding whether the base UGC test is economically justified.

## Cost inputs

All costs must use the same verified currency as the affiliate commission. No FX conversion is guessed.

```json
{
  "costs": {
    "currency": "MXN",
    "production_cost_mxn": 0,
    "sample_cost_mxn": 0,
    "generation_cost_mxn": 200,
    "editing_cost_mxn": 100,
    "other_cost_mxn": 0
  },
  "scenarios": [
    {"name": "conservative", "views": 1000, "ctr": 0.01, "cvr": 0.03},
    {"name": "base", "views": 5000, "ctr": 0.02, "cvr": 0.05},
    {"name": "aggressive", "views": 10000, "ctr": 0.03, "cvr": 0.06}
  ]
}
```

CTR/CVR are assumptions until real history is available. They must be replaced by empirical channel/category/hook baselines as observations accumulate.

## Build the order

```bash
python -m ugc_commerce.cli factory-order \
  --product examples/product-intelligence-input.json \
  --economics examples/factory-production-economics.json \
  --channel cano \
  --angle transformation \
  --angle problem_solution \
  --angle demo \
  --creative-count 3 \
  --output storage/factory-order.json
```

If Product Intelligence is not `PROCEDE`, economics are incomplete, currencies do not match, or base net benefit is negative, no production order is emitted.

The generated order is `READY_FOR_APPROVAL`. Its scope SHA-256 covers product identity, target channel, production mode, creative count, angles, claims, assets, provenance, scores and cost/benefit data.

## Human approval

```bash
python -m ugc_commerce.cli factory-order-approve \
  --order storage/factory-order.json \
  --approved-by Cano \
  --output storage/factory-order-approved.json
```

Agent/system identities cannot self-approve. Any change to scoped production intent invalidates the approval.

The approval authorizes only the exact production order and its explicit test cost. It does not authorize publication, ads or budget scaling.

## Factory handoff

Copy/mount the approved JSON into the Factory V5 runtime and run:

```bash
python scripts/ugc_commerce_bridge.py ingest \
  --order /path/to/factory-order-approved.json \
  --receipt storage/ugc-commerce/factory-receipt.json
```

For `ugc_higgsfield`, Factory materializes one `reel_higgsfield` production job per approved angle and records the upstream human approval as the premium-credit approval for that exact commerce scope. Publication remains separately gated by Factory governance.

## Receipt validation

Back in Commerce:

```bash
python -m ugc_commerce.cli factory-receipt \
  --order storage/factory-order-approved.json \
  --receipt /path/to/factory-receipt.json
```

The receipt must match both `order_id` and `scope_id`.

## Contract versions

- `contracts/commerce-production-order-v1.schema.json`
- `contracts/factory-production-receipt-v1.schema.json`

Breaking changes require a new contract version. Do not silently reinterpret v1 fields.
