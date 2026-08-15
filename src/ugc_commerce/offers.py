from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field

from .domain import ProductManifest


class EvidenceStatus(StrEnum):
    VERIFIED = "VERIFIED"
    INFERRED = "INFERRED"
    ESTIMATED = "ESTIMATED"
    UNKNOWN = "UNKNOWN"


class EvidenceValue(BaseModel):
    value: Any | None = None
    status: EvidenceStatus = EvidenceStatus.UNKNOWN
    source: str | None = None
    verified_at: datetime | None = None

    @classmethod
    def verified(cls, value: Any, *, source: str | None = None, verified_at: datetime | None = None) -> "EvidenceValue":
        return cls(value=value, status=EvidenceStatus.VERIFIED, source=source, verified_at=verified_at)

    @classmethod
    def inferred(cls, value: Any, *, source: str | None = None) -> "EvidenceValue":
        return cls(value=value, status=EvidenceStatus.INFERRED, source=source)

    @classmethod
    def estimated(cls, value: Any, *, source: str | None = None) -> "EvidenceValue":
        return cls(value=value, status=EvidenceStatus.ESTIMATED, source=source)

    @classmethod
    def unknown(cls, *, source: str | None = None) -> "EvidenceValue":
        return cls(value=None, status=EvidenceStatus.UNKNOWN, source=source)

    @property
    def is_known(self) -> bool:
        return self.value is not None and self.status != EvidenceStatus.UNKNOWN

    @property
    def is_verified(self) -> bool:
        return self.value is not None and self.status == EvidenceStatus.VERIFIED


class ProductOfferSnapshot(BaseModel):
    schema_version: str = "1.0"
    platform: str
    market: str = "MX"
    seller_name: str | None = None
    product_id: str
    title: str
    source_url: str | None = None
    affiliate_url: str | None = None

    price_amount: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    currency: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    original_price: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    discount_price: EvidenceValue = Field(default_factory=EvidenceValue.unknown)

    organic_commission_rate: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    organic_commission_amount: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    shop_ads_commission_rate: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    shop_ads_commission_amount: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    displayed_earnings_amount: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    displayed_earnings_currency: EvidenceValue = Field(default_factory=EvidenceValue.unknown)

    free_sample_available: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    sample_status: str = "unknown"
    sample_requirements: list[str] = Field(default_factory=list)

    sales_count: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    orders_count: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    rating: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    review_count: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    stock_status: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    category: str | None = None
    trend_signal: EvidenceValue = Field(default_factory=EvidenceValue.unknown)

    media_assets: list[str] = Field(default_factory=list)
    verified_benefits: list[str] = Field(default_factory=list)
    prohibited_claims: list[str] = Field(default_factory=list)
    commercial_rights_status: Literal["pending", "approved", "rejected"] = "pending"

    requires_medical_claims: bool = False
    has_known_platform_restrictions: bool = False
    has_blocking_platform_restrictions: bool = False
    critical_evidence_conflict: bool = False

    invitation_valid_from: datetime | None = None
    invitation_valid_until: datetime | None = None
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    verified_at: datetime | None = None
    source_provenance: list[str] = Field(default_factory=list)

    @classmethod
    def from_manifest(cls, product: ProductManifest) -> "ProductOfferSnapshot":
        source = "ProductManifest"
        return cls(
            platform=product.platform,
            product_id=product.product_id,
            title=product.title,
            source_url=str(product.source_url) if product.source_url else None,
            affiliate_url=str(product.affiliate_url) if product.affiliate_url else None,
            price_amount=(EvidenceValue.inferred(product.price_amount, source=source) if product.price_amount is not None else EvidenceValue.unknown(source=source)),
            currency=EvidenceValue.inferred(product.currency, source=source),
            organic_commission_amount=(EvidenceValue.inferred(product.commission_value, source=source) if product.commission_value is not None else EvidenceValue.unknown(source=source)),
            stock_status=(EvidenceValue.inferred(product.availability, source=source) if product.availability != "unknown" else EvidenceValue.unknown(source=source)),
            media_assets=list(product.media_assets),
            verified_benefits=list(product.verified_benefits),
            prohibited_claims=list(product.prohibited_claims),
            commercial_rights_status=product.commercial_rights_status,
            source_provenance=[source],
        )
