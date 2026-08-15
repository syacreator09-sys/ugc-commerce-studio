from __future__ import annotations

from hashlib import sha256
from typing import Any

from .base import DiscoveryCandidate, DiscoveryProvider
from ..offers import EvidenceValue, ProductOfferSnapshot


def _candidate_id(payload: dict[str, Any]) -> str:
    if payload.get("product_id"):
        return str(payload["product_id"])
    raw = f"{payload.get('platform','manual')}|{payload.get('seller_name','')}|{payload.get('title','unknown')}"
    return "candidate_" + sha256(raw.encode("utf-8")).hexdigest()[:12]


def _ev(payload: dict[str, Any], key: str, source: str) -> EvidenceValue:
    if key not in payload or payload[key] is None:
        return EvidenceValue.unknown(source=source)
    raw = payload[key]
    if isinstance(raw, dict) and ("status" in raw or "value" in raw):
        return EvidenceValue.model_validate(raw)
    return EvidenceValue.verified(raw, source=source)


class ManualDiscoveryProvider(DiscoveryProvider):
    name = "manual"

    def discover(self, payloads: list[dict[str, Any]]) -> list[DiscoveryCandidate]:
        result: list[DiscoveryCandidate] = []
        for payload in payloads:
            source = str(payload.get("source") or "manual")
            offer = ProductOfferSnapshot(
                platform=str(payload.get("platform") or "unknown"),
                market=str(payload.get("market") or "MX"),
                seller_name=payload.get("seller_name"),
                product_id=_candidate_id(payload),
                title=str(payload.get("title") or "Untitled candidate"),
                source_url=payload.get("source_url"),
                affiliate_url=payload.get("affiliate_url"),
                price_amount=_ev(payload, "price_amount", source),
                currency=_ev(payload, "currency", source),
                original_price=_ev(payload, "original_price", source),
                discount_price=_ev(payload, "discount_price", source),
                organic_commission_rate=_ev(payload, "organic_commission_rate", source),
                organic_commission_amount=_ev(payload, "organic_commission_amount", source),
                shop_ads_commission_rate=_ev(payload, "shop_ads_commission_rate", source),
                shop_ads_commission_amount=_ev(payload, "shop_ads_commission_amount", source),
                displayed_earnings_amount=_ev(payload, "displayed_earnings_amount", source),
                displayed_earnings_currency=_ev(payload, "displayed_earnings_currency", source),
                free_sample_available=_ev(payload, "free_sample_available", source),
                sales_count=_ev(payload, "sales_count", source),
                orders_count=_ev(payload, "orders_count", source),
                rating=_ev(payload, "rating", source),
                review_count=_ev(payload, "review_count", source),
                stock_status=_ev(payload, "stock_status", source),
                trend_signal=_ev(payload, "trend_signal", source),
                category=payload.get("category"),
                media_assets=list(payload.get("media_assets") or []),
                verified_benefits=list(payload.get("verified_benefits") or []),
                prohibited_claims=list(payload.get("prohibited_claims") or []),
                commercial_rights_status=payload.get("commercial_rights_status", "pending"),
                requires_medical_claims=bool(payload.get("requires_medical_claims", False)),
                has_known_platform_restrictions=bool(payload.get("has_known_platform_restrictions", False)),
                has_blocking_platform_restrictions=bool(payload.get("has_blocking_platform_restrictions", False)),
                critical_evidence_conflict=bool(payload.get("critical_evidence_conflict", False)),
                source_provenance=[source],
            )
            result.append(DiscoveryCandidate(provider=self.name, offer=offer, raw=payload))
        return result
