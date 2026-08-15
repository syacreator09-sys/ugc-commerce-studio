# Commerce → Factory Production Bridge Plan

**Goal:** Extend `ugc-commerce-studio` so an affiliate opportunity is converted into a production order only after deterministic cost/benefit analysis, existing product hard gates, and explicit human approval.

## Contract

`CommerceProductionOrderV1` is the versioned boundary. It carries evidence/provenance, economics, target channel, creative count/angles, allowed/prohibited claims, assets, immutable scope ID, and approval metadata. No runtime import from Factory is allowed.

## Tasks

- [ ] Add deterministic production cost/benefit analysis with conservative/base/aggressive scenarios, net benefit, ROI, break-even and explicit `NEEDS_DATA | NOT_ECONOMIC | APPROVAL_REQUIRED` recommendation.
- [ ] Add versioned `CommerceProductionOrderV1` + `FactoryProductionReceiptV1` models and JSON Schemas.
- [ ] Refuse order creation unless `ProductIntelligenceReport.production_decision == PROCEDE`, economics are comparable in one verified currency, and the cost/benefit recommendation is approval-worthy.
- [ ] Require explicit human approval to transition an order from `READY_FOR_APPROVAL` to `APPROVED`; approval must match immutable order scope.
- [ ] Add CLI commands to build, approve and ingest Factory receipts. These commands must not call Higgsfield or publish.
- [ ] Add regression tests for sparse/unknown-currency offers, negative ROI, hard-gated products, approved positive economics, immutable scope, and receipt correlation.
- [ ] Document the bridge and verify compile/tests/CLI smoke.

## Safety

Commerce approval authorizes handoff to Factory production only. It does not authorize publication, ads, budget scaling, or bypass Factory premium-credit gates.