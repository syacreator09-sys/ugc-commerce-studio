from pathlib import Path

from ugc_commerce.distribution import prepare_draft
from ugc_commerce.domain import ProductManifest, UGCProfile
from ugc_commerce.planner import build_plan


def test_tiktok_draft_stays_manual_and_unpublished():
    product = ProductManifest(
        product_id="p1",
        ownership_type="affiliate",
        platform="tiktok_shop",
        title="Producto",
        source_url="https://example.com/product",
        affiliate_url="https://example.com/affiliate",
        availability="available",
        verified_benefits=["beneficio verificado"],
        media_assets=["front.jpg", "side.jpg", "detail.jpg"],
        commercial_rights_status="approved",
    )
    profile = UGCProfile(brand_name="Cano", cta="Revisa el precio")
    draft = prepare_draft(build_plan(product, profile), Path("master.mp4"))
    assert draft.auto_publish is False
    assert draft.manual_product_anchor_required is True
    assert "comisión" in " ".join(draft.disclosures)
