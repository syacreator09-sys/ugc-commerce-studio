from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class OwnershipType(StrEnum):
    OWNED = "owned"
    AFFILIATE = "affiliate"


class ProductManifest(BaseModel):
    schema_version: str = "1.0"
    product_id: str
    ownership_type: OwnershipType
    platform: str
    title: str
    source_url: HttpUrl | None = None
    price_amount: float | None = Field(default=None, ge=0)
    currency: str = "MXN"
    availability: str = "unknown"
    affiliate_url: HttpUrl | None = None
    commission_value: float | None = Field(default=None, ge=0)
    verified_benefits: list[str] = Field(default_factory=list)
    prohibited_claims: list[str] = Field(default_factory=list)
    media_assets: list[str] = Field(default_factory=list)
    commercial_rights_status: Literal["pending", "approved", "rejected"] = "pending"


class UGCProfile(BaseModel):
    brand_name: str
    audience: str = "es_MX"
    cta: str
    language: str = "es-LATAM"
    tone: str = "natural, conversational, trustworthy"
    avatar_id: str | None = None
    avatar_type: Literal["preset", "custom"] = "preset"


class Scene(BaseModel):
    index: int = Field(ge=1)
    goal: str
    natural_text: str
    spoken_text: str
    caption_text: str
    vibe: str
    visual_direction: str
    duration_seconds: int = Field(default=5, ge=4, le=15)


class UGCPlan(BaseModel):
    plan_id: str
    scope_id: str
    created_at: datetime = Field(default_factory=utc_now)
    workflow: Literal["marketing_studio", "direct_scene"]
    mode: str
    model: str
    product: ProductManifest
    profile: UGCProfile
    scenes: list[Scene]
    auto_publish: bool = False
    human_review_required: bool = True

    @classmethod
    def create(cls, *, workflow: str, mode: str, model: str, product: ProductManifest, profile: UGCProfile, scenes: list[Scene]) -> "UGCPlan":
        payload = "|".join([
            workflow,
            mode,
            model,
            product.model_dump_json(),
            profile.model_dump_json(),
            "".join(scene.model_dump_json() for scene in scenes),
        ])
        digest = sha256(payload.encode("utf-8")).hexdigest()
        return cls(
            plan_id=f"plan_{digest[:16]}",
            scope_id=f"scope_{digest}",
            workflow=workflow,
            mode=mode,
            model=model,
            product=product,
            profile=profile,
            scenes=scenes,
        )


class Approval(BaseModel):
    scope_id: str
    approved_by: str
    approved_at: datetime = Field(default_factory=utc_now)
    action: Literal["premium_generation"] = "premium_generation"
