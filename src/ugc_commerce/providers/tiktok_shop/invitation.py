from __future__ import annotations

from hashlib import sha256
from typing import Any

from ...offers import EvidenceValue, ProductOfferSnapshot


def _candidate_id(data: dict[str, Any]) -> str:
    if data.get("product_id"):
        return str(data["product_id"])
    raw = f"{data.get('seller_name','')}|{data.get('title','unknown')}"
    return "tiktok_invitation_" + sha256(raw.encode("utf-8")).hexdigest()[:12]


def _verified_or_unknown(data: dict[str, Any], key: str, source: str) -> EvidenceValue:
    if key in data and data[key] is not None:
        return EvidenceValue.verified(data[key], source=source)
    return EvidenceValue.unknown(source=source)


def _rate(data: dict[str, Any], key: str, source: str) -> EvidenceValue:
    if key not in data or data[key] is None:
        return EvidenceValue.unknown(source=source)
    value = data[key]
    if isinstance(value, str):
        text = value.strip()
        if text.endswith("%"):
            try:
                value = float(text[:-1].strip()) / 100
            except ValueError:
                return EvidenceValue.unknown(source=source)
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return EvidenceValue.unknown(source=source)
    if not 0 <= numeric <= 1:
        return EvidenceValue.unknown(source=source)
    return EvidenceValue.verified(numeric, source=source)


def normalize_tiktok_invitation(data: dict[str, Any], *, source: str = "tiktok_invitation") -> ProductOfferSnapshot:
    """Normalize evidence already extracted from TikTok UI/API into the canonical offer model.

    This adapter does not scrape TikTok and never infers missing price, currency,
    commission, demand, stock, or platform rules.
    """
    return ProductOfferSnapshot(
        platform="tiktok_shop",
        market=str(data.get("market") or "MX"),
        seller_name=data.get("seller_name"),
        product_id=_candidate_id(data),
        title=str(data.get("title") or "TikTok Shop invitation"),
        source_url=data.get("source_url"),
        affiliate_url=data.get("affiliate_url"),
        price_amount=_verified_or_unknown(data, "price_amount", source),
        currency=_verified_or_unknown(data, "currency", source),
        organic_commission_rate=_rate(data, "organic_commission_rate", source),
        organic_commission_amount=_verified_or_unknown(data, "organic_commission_amount", source),
        shop_ads_commission_rate=_rate(data, "shop_ads_commission_rate", source),
        shop_ads_commission_amount=_verified_or_unknown(data, "shop_ads_commission_amount", source),
        displayed_earnings_amount=_verified_or_unknown(data, "displayed_earnings_amount", source),
        displayed_earnings_currency=_verified_or_unknown(data, "displayed_earnings_currency", source),
        free_sample_available=_verified_or_unknown(data, "free_sample_available", source),
        sample_status=str(data.get("sample_status") or "unknown"),
        sample_requirements=list(data.get("sample_requirements") or []),
        sales_count=_verified_or_unknown(data, "sales_count", source),
        orders_count=_verified_or_unknown(data, "orders_count", source),
        rating=_verified_or_unknown(data, "rating", source),
        review_count=_verified_or_unknown(data, "review_count", source),
        stock_status=_verified_or_unknown(data, "stock_status", source),
        category=data.get("category"),
        trend_signal=_verified_or_unknown(data, "trend_signal", source),
        media_assets=list(data.get("media_assets") or []),
        verified_benefits=list(data.get("verified_benefits") or []),
        prohibited_claims=list(data.get("prohibited_claims") or []),
        commercial_rights_status=data.get("commercial_rights_status", "pending"),
        requires_medical_claims=bool(data.get("requires_medical_claims", False)),
        has_known_platform_restrictions=bool(data.get("has_known_platform_restrictions", False)),
        has_blocking_platform_restrictions=bool(data.get("has_blocking_platform_restrictions", False)),
        critical_evidence_conflict=bool(data.get("critical_evidence_conflict", False)),
        invitation_valid_from=data.get("invitation_valid_from"),
        invitation_valid_until=data.get("invitation_valid_until"),
        source_provenance=[source],
    )
