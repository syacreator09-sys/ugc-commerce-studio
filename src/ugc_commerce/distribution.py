from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from .domain import ProductManifest, UGCPlan


class PublicationDraft(BaseModel):
    draft_id: str
    platform: str
    product_id: str
    master_path: str
    caption: str
    destination_url: str | None = None
    disclosures: list[str] = Field(default_factory=list)
    manual_product_anchor_required: bool = False
    auto_publish: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def prepare_draft(plan: UGCPlan, master: Path) -> PublicationDraft:
    product: ProductManifest = plan.product
    platform = product.platform.lower()
    disclosures = ["Contenido generado o modificado con IA", "Contenido comercial"]
    manual_anchor = platform in {"tiktok", "tiktok_shop"}

    destination = str(product.affiliate_url or product.source_url) if (product.affiliate_url or product.source_url) else None
    caption = f"{product.title}. {plan.profile.cta}"
    if product.ownership_type == "affiliate":
        disclosures.append("El enlace puede generar una comisión")

    return PublicationDraft(
        draft_id=f"draft_{plan.plan_id}",
        platform=product.platform,
        product_id=product.product_id,
        master_path=str(master),
        caption=caption,
        destination_url=destination,
        disclosures=disclosures,
        manual_product_anchor_required=manual_anchor,
        auto_publish=False,
    )
