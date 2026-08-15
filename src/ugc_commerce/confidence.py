from __future__ import annotations

from pydantic import BaseModel, Field

from .offers import EvidenceStatus, EvidenceValue, ProductOfferSnapshot


class ConfidenceReport(BaseModel):
    score: int = Field(ge=0, le=100)
    missing_data: list[str] = Field(default_factory=list)
    deductions: dict[str, int] = Field(default_factory=dict)


def _known(value: EvidenceValue) -> bool:
    return value.value is not None and value.status != EvidenceStatus.UNKNOWN


def _verified(value: EvidenceValue) -> bool:
    return value.value is not None and value.status == EvidenceStatus.VERIFIED


def assess_data_confidence(offer: ProductOfferSnapshot) -> ConfidenceReport:
    score = 100
    missing: list[str] = []
    deductions: dict[str, int] = {}

    def deduct(key: str, amount: int, missing_key: str | None = None) -> None:
        nonlocal score
        if key in deductions:
            return
        score -= amount
        deductions[key] = amount
        if missing_key and missing_key not in missing:
            missing.append(missing_key)

    if not _known(offer.currency):
        deduct("unknown_currency", 15, "currency")
    elif not _verified(offer.currency):
        deduct("unverified_currency", 5)

    if not _known(offer.price_amount):
        deduct("unknown_price", 15, "price")
    elif not _verified(offer.price_amount):
        deduct("unverified_price", 5)

    commission_known = _known(offer.organic_commission_amount) or _known(offer.organic_commission_rate)
    commission_verified = _verified(offer.organic_commission_amount) or _verified(offer.organic_commission_rate)
    if not commission_known:
        deduct("unknown_organic_commission", 20, "organic_commission")
    elif not commission_verified:
        deduct("unverified_organic_commission", 7)

    if not _known(offer.stock_status):
        deduct("unknown_stock", 10, "stock")
    elif not _verified(offer.stock_status):
        deduct("unverified_stock", 4)

    demand_known = _known(offer.sales_count) or _known(offer.orders_count) or _known(offer.review_count) or _known(offer.rating)
    demand_verified = _verified(offer.sales_count) or _verified(offer.orders_count) or _verified(offer.review_count) or _verified(offer.rating)
    if not demand_known:
        deduct("unknown_demand", 15, "demand")
    elif not demand_verified:
        deduct("unverified_demand", 5)

    if not offer.source_provenance:
        deduct("missing_provenance", 5)

    if offer.critical_evidence_conflict:
        deduct("critical_evidence_conflict", 30)

    return ConfidenceReport(score=max(0, min(100, score)), missing_data=missing, deductions=deductions)
