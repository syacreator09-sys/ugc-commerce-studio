# UGC Commerce Operating Engine — Design

**Date:** 2026-08-14  
**Repository:** `syacreator09-sys/ugc-commerce-studio`  
**Status:** proposed for implementation

## Decision

Do **not** create a new repository. `ugc-commerce-studio` becomes the canonical UGC affiliate commerce engine. `cano-ai-command-center/01-offices/ugc-affiliate` remains a control/orchestration surface and legacy reference only; no runtime dependency is introduced from the canonical engine back to the Command Center.

## Goal

Build one reusable engine that can discover affiliate products, normalize and verify evidence, calculate deterministic economics and UGC fit, decide whether to request samples and produce content, generate UGC through the existing Higgsfield pipeline, track real performance, learn from historical outcomes, and scale winning creative angles.

## Non-goals

- No new repository.
- No second UGC production engine.
- No automatic publishing.
- No automatic ad activation or budget scaling.
- No replacement of the existing Higgsfield production path.
- No ML system in v1; historical learning starts with deterministic aggregation and baselines.
- No hardcoded mutable TikTok rules or commission assumptions presented as facts.

## Existing constraints preserved

The existing repository rules remain authoritative:

- `auto_publish=false`
- `auto_activate_ads=false`
- `auto_scale_budget=false`
- `human_review_required=true`
- `premium_generation_requires_approval=true`
- `publication_mode=draft_only`
- Higgsfield remains the only premium generation provider.
- Exact product media is the source of truth.
- AI and commercial disclosures remain required where applicable.
- Product rights, price, stock, commission, claims and evidence must be validated before premium generation.

## Architecture

```text
Discovery Sources
      ↓
ProductOfferSnapshot
      ↓
Evidence / Provenance Validator
      ↓
┌───────────────┬────────────────────┬─────────────────┐
│ UGC Fit Engine│ Economics Engine   │ Demand Signals  │
└───────────────┴────────────────────┴─────────────────┘
      ↓
Confidence / Data Quality
      ↓
Decision Engine
      ↓
Sample Decision + Production Decision
      ↓
Creative Strategy / Test Matrix
      ↓
Exact Scope Approval
      ↓
Existing Higgsfield Production
      ↓
QA + Draft Packaging
      ↓
Publication Event / Tracking
      ↓
Performance Analytics
      ↓
Historical Learning
      ↓
Scale / Hold / Kill Recommendation
```

## Responsibility boundaries

### 1. Discovery

Discovers candidate offers without generating content. Providers are adapters, not business logic.

Initial supported sources:

- TikTok Shop candidate data supplied by URL, copied text, screenshots interpreted by an LLM, or provider-specific discovery adapter.
- TikTok seller invitations / free sample invitations.
- Mercado Libre affiliate candidates as a secondary adapter.
- Manual product input.
- Legacy discovery logic from `cano-ai-command-center/01-offices/ugc-affiliate` may be audited and migrated only when still valid.

Discovery output is a normalized `ProductOfferSnapshot`; discovery must not decide whether a product is worth producing.

### 2. Evidence and provenance

Every important commercial value carries provenance and confidence.

Conceptual representation:

```text
value
status: VERIFIED | INFERRED | ESTIMATED | UNKNOWN
source
verified_at
```

The engine must never convert an ambiguous displayed value into a verified fact. Example: a screenshot showing `Earn $181.90` without an explicit currency produces amount `181.90`, currency `UNKNOWN`, and partial confidence.

### 3. Product model

Introduce a backwards-compatible offer model around the existing `ProductManifest`.

Core fields include:

- platform / market / seller
- product identifiers and source URL
- current/original/discount price and currency
- organic commission rate and amount
- Shop Ads commission rate and amount
- displayed earnings amount and displayed currency
- free-sample availability, status and requirements
- sales/orders, rating, review count, stock
- category and trend signal
- product media and verified benefits
- prohibited claims
- invitation validity window
- captured/verified timestamps
- source provenance

Existing `ProductManifest` commands and workflows continue to work.

### 4. UGC Fit

Preserve the current deterministic `product_scout_score` behavior but make its real scale explicit.

The existing documented axes sum to a maximum raw score of 90, not 100. Therefore the engine exposes:

```text
ugc_fit_raw_score: 0..90
ugc_fit_normalized_score: raw / 90 * 100
```

Historical thresholds are not silently changed. Any normalized thresholds must be versioned separately.

UGC Fit evaluates:

- comprehension within ~3 seconds
- visual demonstration / transformation
- photogenic quality
- channel fit
- common pain solved
- impulse potential
- trend signal
- production difficulty
- product fidelity risk
- claim risk
- creative diversity

### 5. Economics

All arithmetic is deterministic Python, never free-form LLM math.

Organic and Shop Ads commission are independent.

```text
organic_commission_per_sale = verified amount
or price × verified organic rate

shop_ads_commission_per_sale = price × verified Shop Ads rate
```

If required inputs are missing, the value is `UNKNOWN` rather than estimated unless an explicit scenario assumption is provided.

Scenario math:

```text
clicks = views × CTR
orders = views × CTR × CVR
affiliate_revenue = orders × commission_per_sale
expected_orders_per_1000_views = 1000 × CTR × CVR
commission_per_1000_views = 1000 × CTR × CVR × commission_per_sale
```

CTR/CVR are decimal values (`2% == 0.02`).

Production economics can include optional sample, generation, editing and other costs. Break-even orders are calculated only with a positive verified/explicit commission-per-sale.

The historical metric `commission / views` is named `commission_per_view` or `revenue_per_view`, not CPV.

### 6. Confidence / data quality

A separate `0..100` confidence score measures evidence quality. It penalizes unknown or stale values, inferred commissions, unknown currency, missing demand data, missing stock, contradictions and unverified platform facts.

High UGC fit with low confidence must not become a confident production recommendation.

### 7. Decision engine

Two independent decisions are returned:

```text
sample_decision: SOLICITAR | NO_SOLICITAR | NEEDS_DATA
production_decision: PROCEDE | EN_ESPERA | RECHAZADO
```

Hard gates execute before commercial scoring. Examples:

- prohibited category
- regulated/medical claim requiring unsupported claims
- rejected commercial rights
- critical evidence conflict
- platform restriction that makes the offer non-viable

A high commission cannot override a hard gate.

### 8. Creative capacity

Add a deterministic/structured `creative_capacity_score` based on genuinely distinct:

- hooks
- audiences
- use cases
- demonstrations
- objections
- transformations
- review/tutorial/POV/comparison/problem-solution angles

The engine recommends an initial test count such as `0`, `1`, `3`, `5`, or `10+`, but avoids large batches before signal exists.

Default strategy:

```text
test small → measure → identify winner → multiply winning angle
```

### 9. Production

The existing Higgsfield pipeline remains responsible for generation after intelligence and approval.

```text
Intelligence decides
Creative strategy designs
Higgsfield executes
QA verifies
```

No product-intelligence module should directly spend premium credits.

### 10. Analytics

Tracking should support stable identifiers for product, offer, creative, hook, video and publication.

Core post-publication metrics:

- views
- retention / watch-time metrics when available
- product clicks
- CTR
- orders
- CVR
- GMV
- organic commission
- Shop Ads commission
- total commission
- commission per view
- commission per 1,000 views
- commission per order

Zero denominators are handled safely.

### 11. Learning

Persist enough historical structure to replace assumptions with our own real baselines over time.

Initial dimensions:

- channel
- category
- product price band
- hook
- format
- avatar/presenter
- UGC angle
- seller/product

V1 uses deterministic aggregation and rolling historical baselines, not a machine-learning model.

## Proposed package boundaries

Follow the repository's current compact Python style rather than performing a large unrelated restructure. New focused modules may be introduced under `src/ugc_commerce/`:

```text
offers.py                 normalized offer/evidence models
economics.py              deterministic affiliate math
confidence.py             data-quality scoring
decisions.py              hard gates and decisions
creative_capacity.py      test-count recommendation
performance.py            post-publication metrics
history.py                historical aggregates / baselines
discovery/                provider-neutral discovery interfaces
providers/tiktok_shop/    TikTok-specific adapter(s)
providers/mercadolibre/   optional secondary adapter(s)
```

Existing modules (`domain.py`, `intelligence.py`, `product_scout_score.py`, `planner.py`, `higgsfield.py`, `distribution.py`, `sources.py`) stay in place unless a targeted migration is required.

## Command-line surface

Existing commands remain backwards-compatible. New commands are additive, conceptually:

```bash
python -m ugc_commerce.cli scout --product product.json
python -m ugc_commerce.cli economics --product product.json --views 1000 --ctr 0.02 --cvr 0.05
python -m ugc_commerce.cli discover --source tiktok_shop
```

Exact flags should match the current CLI parser conventions.

## Agent boundary

LLMs are used for tasks that require interpretation:

```text
LLM extracts evidence from URL/text/screenshot
→ deterministic engine validates and calculates
→ LLM explains/recommends using engine output
→ human approves premium generation
```

LLMs must not fabricate price, currency, commission, sales, stock or platform rules.

## Canonical report

A Product Intelligence Report exposes at least:

```text
PRODUCT
DATA QUALITY
ECONOMICS
UGC FIT
CREATIVE CAPACITY
DEMAND
RISK
SAMPLE DECISION
PRODUCTION DECISION
WHY
MISSING DATA
NEXT ACTION
```

All projections include assumptions, confidence and source provenance.

## Required regression case

A required fixture models an invitation with only:

```text
free_sample = true
displayed_earnings_amount = 181.90
displayed_earnings_currency = UNKNOWN
shop_ads_commission_rate = 0.01
price = UNKNOWN
sales = UNKNOWN
reviews = UNKNOWN
```

Expected behavior:

- Do not claim `181.90 MXN`.
- Do not calculate Shop Ads commission-per-sale without price.
- Mark missing currency, price, organic commission verification and demand evidence.
- Return partial/low economics confidence.
- Use a conservative sample decision (`NEEDS_DATA` unless policy explicitly permits a free-sample exploratory request).

## Testing strategy

Use TDD for each deterministic component. Preserve all existing tests and add targeted tests for:

- organic commission by amount/rate
- organic vs Shop Ads separation
- unknown price/currency/commission
- displayed earnings without currency
- decimal CTR/CVR handling
- expected orders and commission per 1K views
- break-even and zero division
- free-sample decisioning
- hard rejects
- confidence scoring
- raw 0–90 and normalized 0–100 UGC fit
- creative-count recommendation
- analytics metrics
- backwards compatibility of `ProductManifest`, planning and Higgsfield flows

Final verification remains:

```bash
python -m compileall -q src scripts
pytest -q
python scripts/doctor.py
```

## Migration from Command Center

`cano-ai-command-center/01-offices/ugc-affiliate` is audited as a legacy source. Only verified useful behavior is migrated:

- product discovery ideas/adapters
- recommender logic
- commission estimator concepts (never as unverified facts)
- performance tracking concepts
- sales dashboard metrics
- TikTok-specific operational knowledge with provenance/date stamps

Do not copy stale paths, hardcoded credentials, obsolete model references or old infrastructure assumptions.

After migration, Command Center should call or instruct `ugc-commerce-studio`; it should not maintain a competing implementation.

## Success criteria

The repository can take a candidate affiliate product, preserve what is known vs unknown, calculate UGC fit and economics deterministically, decide whether more data/sample/production is justified, generate only after exact approval, track real outcomes, and use those outcomes to recommend which products and creative angles to scale—without creating a second repository or duplicating the existing production engine.
