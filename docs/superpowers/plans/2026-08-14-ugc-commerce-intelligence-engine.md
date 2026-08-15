# UGC Commerce Intelligence Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert `ugc-commerce-studio` into the canonical affiliate UGC operating engine for evidence-aware product intelligence, deterministic economics, sample/production decisions, creative test sizing, analytics, learning, and provider-neutral discovery without replacing the existing Higgsfield production path.

**Architecture:** Keep the current compact package and add focused deterministic modules under `src/ugc_commerce/`. LLMs/providers extract evidence into typed snapshots; Python performs calculations and decisions; existing approval/Higgsfield generation stays downstream. Legacy `cano-ai-command-center/01-offices/ugc-affiliate` is reference-only and never a runtime dependency.

**Tech Stack:** Python 3.11+, Pydantic 2, Typer, pytest, jsonschema, existing Higgsfield CLI integration.

## Global Constraints

- Do not create a new repository or second production engine.
- Preserve `ProductManifest`, planning, approval, Higgsfield pilot, and draft-only behavior.
- `auto_publish=false`, `auto_activate_ads=false`, `auto_scale_budget=false`, `human_review_required=true`, `premium_generation_requires_approval=true`, `publication_mode=draft_only`.
- Never turn ambiguous commercial values into verified facts.
- Organic commission and Shop Ads commission are independent.
- Deterministic math lives in Python, not prompts.
- UGC legacy raw score remains 0..90; expose normalization separately as `raw / 90 * 100` without silently changing historical thresholds.
- Mutable platform rules are data/provenance, not hardcoded permanent facts.
- Use TDD for production behavior changes.

---

### Task 1: Evidence-aware offer domain

**Files:**
- Create: `src/ugc_commerce/offers.py`
- Create: `tests/test_offers.py`
- Create: `contracts/product-offer-snapshot.schema.json`

**Interfaces:**
- Produces: `EvidenceStatus`, `EvidenceValue`, `ProductOfferSnapshot`, and a backwards-compatible converter from `ProductManifest`.
- Consumes: existing `ProductManifest` from `domain.py`.

- [ ] **Step 1:** Write failing tests for unknown currency, explicit verified values, and `ProductManifest` conversion.
- [ ] **Step 2:** Run `pytest tests/test_offers.py -q` and confirm RED because `ugc_commerce.offers` does not exist.
- [ ] **Step 3:** Implement minimal Pydantic models. `EvidenceValue.status` is `VERIFIED | INFERRED | ESTIMATED | UNKNOWN`; unknown commercial values remain unknown. Include price, organic commission, Shop Ads commission, displayed earnings, free sample, demand, stock, invitation, timestamps, provenance, media and claim fields.
- [ ] **Step 4:** Run `pytest tests/test_offers.py -q` and confirm GREEN.
- [ ] **Step 5:** Add JSON Schema mirroring the public offer contract.

### Task 2: Deterministic affiliate economics

**Files:**
- Create: `src/ugc_commerce/economics.py`
- Create: `tests/test_economics.py`
- Create: `contracts/affiliate-economics.schema.json`

**Interfaces:**
- Produces: `EconomicsScenario`, `AffiliateEconomics`, `calculate_affiliate_economics(snapshot, scenarios, costs)`.
- Consumes: `ProductOfferSnapshot`.

- [ ] **Step 1:** Write failing tests for verified amount, rate × price, Shop Ads separation, unknown price, unknown commission, decimal CTR/CVR, expected orders, commission/1K views, break-even, zero division, and the `$181.90`/unknown-currency regression.
- [ ] **Step 2:** Run `pytest tests/test_economics.py -q` and confirm RED.
- [ ] **Step 3:** Implement commission-per-sale resolution with strict evidence rules; only explicit scenario assumptions may produce projections.
- [ ] **Step 4:** Implement `clicks = views*ctr`, `orders = views*ctr*cvr`, affiliate revenue, expected orders/1K views, commission/1K views, optional test costs and `ceil(cost/commission_per_sale)` break-even.
- [ ] **Step 5:** Run economics tests and confirm GREEN.
- [ ] **Step 6:** Add the economics JSON Schema.

### Task 3: UGC fit normalization, confidence, creative capacity and decisions

**Files:**
- Modify: `src/ugc_commerce/product_scout_score.py`
- Create: `src/ugc_commerce/confidence.py`
- Create: `src/ugc_commerce/creative_capacity.py`
- Create: `src/ugc_commerce/decisions.py`
- Create: `tests/test_confidence.py`
- Create: `tests/test_creative_capacity.py`
- Create: `tests/test_decisions.py`
- Modify: `tests/test_product_scout_score.py`

**Interfaces:**
- Produces: normalized UGC score, `ConfidenceReport`, `CreativeCapacityReport`, `SampleDecision`, `ProductionDecision`, `DecisionReport`.
- Consumes: offer snapshot, existing `ProductScoutScore`, economics result.

- [ ] **Step 1:** Add failing tests proving legacy total/threshold behavior remains unchanged while normalized score exposes 0..100.
- [ ] **Step 2:** Implement normalized score property/helper without changing legacy decisions.
- [ ] **Step 3:** Write failing confidence tests for unknown currency, price, commission, stock, sales/reviews, inferred evidence and contradictions.
- [ ] **Step 4:** Implement deterministic 0..100 data-quality scoring plus missing-data reasons.
- [ ] **Step 5:** Write failing creative-capacity tests for low/medium/high distinct-angle sets and recommended counts `0/1/3/5/10+`.
- [ ] **Step 6:** Implement creative-capacity scoring based on unique hooks, audiences, use cases, demos, objections, transformations and formats.
- [ ] **Step 7:** Write failing decision tests for free-sample `NEEDS_DATA`, strong verified candidate `SOLICITAR`, medical hard reject, rejected rights, low confidence `EN_ESPERA`, and no high-commission override of hard gates.
- [ ] **Step 8:** Implement the decision engine.
- [ ] **Step 9:** Run all new/changed tests and confirm GREEN.

### Task 4: Canonical Product Intelligence report

**Files:**
- Create: `src/ugc_commerce/product_intelligence.py`
- Create: `tests/test_product_intelligence.py`
- Create: `contracts/product-intelligence-report.schema.json`
- Modify: `src/ugc_commerce/intelligence.py`

**Interfaces:**
- Produces: `ProductIntelligenceReport` and `analyze_product_offer(...)`.
- Consumes: offer/economics/confidence/scout/creative-capacity/decisions.

- [ ] **Step 1:** Write failing end-to-end unit tests for a complete strong product, a sparse invitation, and a medical hard-gate product.
- [ ] **Step 2:** Implement the canonical report sections: product, data quality, economics, UGC fit, creative capacity, demand, risk, sample decision, production decision, reasons, missing data, next action.
- [ ] **Step 3:** Keep `intelligence.opportunity_score()` backwards-compatible; do not silently replace current planning semantics.
- [ ] **Step 4:** Run report tests and confirm GREEN.
- [ ] **Step 5:** Add JSON Schema for report serialization.

### Task 5: Analytics and learning primitives

**Files:**
- Create: `src/ugc_commerce/performance.py`
- Create: `src/ugc_commerce/history.py`
- Create: `tests/test_performance.py`
- Create: `tests/test_history.py`

**Interfaces:**
- Produces: publication-performance metrics and deterministic historical baselines/recommendations.

- [ ] **Step 1:** Write failing tests for CTR, CVR, commission/view, commission/1K views, commission/order and safe zero denominators.
- [ ] **Step 2:** Implement correct metric names; do not call commission/views `CPV`.
- [ ] **Step 3:** Write failing tests aggregating by category, channel, hook/format and choosing empirical baselines only when observations exist.
- [ ] **Step 4:** Implement simple deterministic historical aggregation; no ML.
- [ ] **Step 5:** Run tests and confirm GREEN.

### Task 6: Provider-neutral discovery boundary

**Files:**
- Create: `src/ugc_commerce/discovery/__init__.py`
- Create: `src/ugc_commerce/discovery/base.py`
- Create: `src/ugc_commerce/discovery/manual.py`
- Create: `src/ugc_commerce/providers/__init__.py`
- Create: `src/ugc_commerce/providers/tiktok_shop/__init__.py`
- Create: `src/ugc_commerce/providers/tiktok_shop/invitation.py`
- Create: `tests/test_discovery.py`

**Interfaces:**
- Produces: `DiscoveryProvider`, `DiscoveryCandidate`, manual JSON/text-normalized discovery and TikTok invitation normalization.
- Does not scrape private pages or invent current platform data.

- [ ] **Step 1:** Write failing tests that normalize manual structured data and the sparse TikTok invitation regression into `ProductOfferSnapshot` without assigning an unknown currency.
- [ ] **Step 2:** Implement provider-neutral discovery interfaces and the manual provider.
- [ ] **Step 3:** Implement TikTok invitation normalization as a pure adapter over already-extracted evidence. Do not hardcode current commission rules.
- [ ] **Step 4:** Run discovery tests and confirm GREEN.

### Task 7: CLI integration and backwards compatibility

**Files:**
- Modify: `src/ugc_commerce/cli.py`
- Create/Modify: `tests/test_cli_intelligence.py`

**Interfaces:**
- Adds `scout`, `economics`, and `discover` commands without changing existing command behavior.

- [ ] **Step 1:** Write failing Typer CLI tests for the three additive commands.
- [ ] **Step 2:** Implement `scout --product`, `economics --product --views --ctr --cvr`, and `discover --source manual|tiktok_invitation` using JSON files as deterministic inputs.
- [ ] **Step 3:** Ensure commands serialize typed results and never trigger Higgsfield generation.
- [ ] **Step 4:** Run CLI tests and all existing tests.

### Task 8: Documentation, agent contracts and final verification

**Files:**
- Modify: `README.md`
- Modify: `SKILL.md`
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`
- Modify: `agents/product-intelligence-agent.md`
- Modify: `agents/ugc-commerce-orchestrator.md`
- Create: `workflow/04-product-intelligence.md`
- Create: `examples/tiktok-invitation-sparse.json`

**Interfaces:**
- Documents the boundary `LLM extracts evidence → deterministic engine calculates → human approves → Higgsfield produces → analytics closes loop`.

- [ ] **Step 1:** Update docs and agents to route discovery/intelligence through the canonical engine and preserve exact approval before premium generation.
- [ ] **Step 2:** Add sparse TikTok invitation example matching the regression case.
- [ ] **Step 3:** Run final verification: `python -m compileall -q src scripts`, `pytest -q`, `python scripts/doctor.py`.
- [ ] **Step 4:** Manually exercise: complete product, sparse product, displayed earnings without currency, organic+Shop Ads, medical hard gate.
- [ ] **Step 5:** Compare branch to `main`, review for secrets/stale legacy assumptions, then prepare integration report.
