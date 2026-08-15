from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .offers import ProductOfferSnapshot
from .product_intelligence import ProductIntelligenceReport
from .production_economics import CostBenefitRecommendation, ProductionBenefitReport


class CommerceOrderStatus(StrEnum):
    READY_FOR_APPROVAL = "READY_FOR_APPROVAL"
    APPROVED = "APPROVED"


class CommerceProductionMode(StrEnum):
    UGC_HIGGSFIELD = "ugc_higgsfield"
    AUTO_RECOMMENDED = "auto_recommended"
    ECONOMY = "economy"


class CommerceProductionOrderV1(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    order_id: str
    scope_id: str
    status: CommerceOrderStatus = CommerceOrderStatus.READY_FOR_APPROVAL
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved_by: str | None = None
    approved_at: datetime | None = None

    product_id: str
    title: str
    platform: str
    market: str
    seller_name: str | None = None
    source_url: str | None = None
    target_channel: str
    production_mode: CommerceProductionMode = CommerceProductionMode.UGC_HIGGSFIELD

    creative_count: int = Field(ge=1, le=10)
    angles: list[str] = Field(min_length=1)
    verified_claims: list[str] = Field(default_factory=list)
    prohibited_claims: list[str] = Field(default_factory=list)
    media_assets: list[str] = Field(default_factory=list)
    provenance: list[str] = Field(default_factory=list)

    confidence_score: int = Field(ge=0, le=100)
    ugc_fit_raw_score: int = Field(ge=0, le=90)
    ugc_fit_normalized_score: float = Field(ge=0, le=100)
    economics: ProductionBenefitReport

    @model_validator(mode="after")
    def validate_order(self) -> "CommerceProductionOrderV1":
        if len(set(self.angles)) < self.creative_count:
            raise ValueError("creative_count requires at least that many distinct angles")
        if self.status == CommerceOrderStatus.APPROVED and (not self.approved_by or self.approved_at is None):
            raise ValueError("approved orders require approved_by and approved_at")
        return self


class FactoryProductionReceiptV1(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    order_id: str
    scope_id: str
    factory: str = "factory-ia-channel-v5"
    status: str
    production_job_ids: list[int] = Field(default_factory=list)
    idea_ids: list[int] = Field(default_factory=list)
    additional_approval_required: bool = False
    additional_approval_gates: list[str] = Field(default_factory=list)
    received_at: datetime | None = None
    message: str = ""


def _scope_payload(order: CommerceProductionOrderV1 | dict) -> dict:
    if isinstance(order, CommerceProductionOrderV1):
        payload = order.model_dump(mode="json")
    else:
        payload = dict(order)
    for key in ("order_id", "scope_id", "status", "created_at", "approved_by", "approved_at"):
        payload.pop(key, None)
    return payload


def compute_order_scope(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_order_scope(order: CommerceProductionOrderV1) -> bool:
    return order.scope_id == compute_order_scope(_scope_payload(order))


def build_factory_order(
    *,
    offer: ProductOfferSnapshot,
    intelligence: ProductIntelligenceReport,
    economics: ProductionBenefitReport,
    target_channel: str,
    angles: list[str],
    creative_count: int | None = None,
    production_mode: CommerceProductionMode = CommerceProductionMode.UGC_HIGGSFIELD,
) -> CommerceProductionOrderV1:
    if intelligence.product_id != offer.product_id:
        raise ValueError("intelligence report does not match offer product_id")
    if intelligence.production_decision != "PROCEDE":
        raise ValueError("product intelligence has not approved production")
    if economics.recommendation != CostBenefitRecommendation.APPROVAL_REQUIRED:
        raise ValueError("cost/benefit is not ready for human approval")

    recommended = intelligence.recommended_initial_creatives
    if creative_count is None:
        creative_count = int(recommended) if isinstance(recommended, int) and recommended > 0 else min(3, len(angles))
    if creative_count < 1 or creative_count > 10:
        raise ValueError("creative_count must be between 1 and 10")
    distinct_angles = list(dict.fromkeys(angle.strip() for angle in angles if angle.strip()))
    if len(distinct_angles) < creative_count:
        raise ValueError("not enough distinct creative angles for requested creative_count")

    payload = {
        "schema_version": "1.0",
        "product_id": offer.product_id,
        "title": offer.title,
        "platform": offer.platform,
        "market": offer.market,
        "seller_name": offer.seller_name,
        "source_url": offer.source_url,
        "target_channel": target_channel,
        "production_mode": production_mode.value,
        "creative_count": creative_count,
        "angles": distinct_angles[:creative_count],
        "verified_claims": list(offer.verified_benefits),
        "prohibited_claims": list(offer.prohibited_claims),
        "media_assets": list(offer.media_assets),
        "provenance": list(dict.fromkeys(offer.source_provenance)),
        "confidence_score": intelligence.confidence_score,
        "ugc_fit_raw_score": intelligence.ugc_fit_raw_score,
        "ugc_fit_normalized_score": intelligence.ugc_fit_normalized_score,
        "economics": economics.model_dump(mode="json"),
    }
    scope_id = compute_order_scope(payload)
    return CommerceProductionOrderV1(
        order_id=f"cpo-{scope_id[:20]}",
        scope_id=scope_id,
        **payload,
    )


def approve_factory_order(order: CommerceProductionOrderV1, *, approved_by: str) -> CommerceProductionOrderV1:
    actor = approved_by.strip()
    if not actor:
        raise ValueError("approved_by is required")
    if actor.lower() in {"system", "agent", "claude", "codex", "automation"}:
        raise ValueError("approved_by must identify a human approver")
    if not verify_order_scope(order):
        raise ValueError("order scope does not match immutable production intent")
    return order.model_copy(update={
        "status": CommerceOrderStatus.APPROVED,
        "approved_by": actor,
        "approved_at": datetime.now(timezone.utc),
    })


def validate_factory_receipt(order: CommerceProductionOrderV1, receipt: FactoryProductionReceiptV1) -> None:
    if receipt.order_id != order.order_id or receipt.scope_id != order.scope_id:
        raise ValueError("factory receipt does not correlate to the approved commerce order")
