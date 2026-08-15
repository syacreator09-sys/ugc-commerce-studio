# Legacy discovery migration audit

## Scope

Reference source: `syacreator09-sys/cano-ai-command-center/01-offices/ugc-affiliate`.

The legacy `CLAUDE.md` describes discovery components such as:

- `scripts/product_search.py`
- `scripts/daily_run.py`
- `scripts/tiktok_api_discovery.py`
- `scripts/rapidapi_client.py`
- `scripts/commission_estimator.py`
- Android-farm scrapers

At the time of this migration, those script paths are referenced by the Command Center documentation but are **not present in the current GitHub snapshot at those paths**. The current remote office exposes agent/config documentation, not the executable legacy discovery implementation described by that document.

## Decision

Do not recreate or copy an unverified legacy scraper from prose.

`ugc-commerce-studio` v0.5 therefore implements the safe canonical discovery boundary first:

```text
provider/source extracts evidence
→ ProductOfferSnapshot
→ deterministic Product Intelligence
```

Included adapters:

- manual structured evidence;
- TikTok Shop invitation evidence already extracted from UI/API/text/screenshot.

These adapters never infer missing currency, price, organic commission, demand or mutable platform rules.

## Live discovery status

A live authenticated TikTok Shop catalog/invitation crawler is **not claimed as implemented** in v0.5. Adding one requires a currently verifiable source/API/browser workflow plus credentials/auth available to the runtime. It must implement the provider-neutral `DiscoveryProvider` boundary and output evidence with provenance.

Until then, a control plane such as `cano-ai-command-center`, Claude/Codex browser tooling, or another verified provider may discover candidates and feed structured evidence into `ugc-commerce-studio` without creating a runtime dependency back to the Command Center.

## Why

This avoids three failure modes:

1. silently depending on stale or missing RapidAPI assumptions;
2. pretending a private/authenticated TikTok workflow is stable when it has not been verified;
3. contaminating deterministic economics with guessed data from a brittle scraper.

The canonical engine is ready to accept a live provider later without changing scoring, economics, decisioning, production or analytics modules.
