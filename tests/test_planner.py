from ugc_commerce.domain import ProductManifest, UGCProfile
from ugc_commerce.planner import build_plan


def product() -> ProductManifest:
    return ProductManifest(
        product_id="prod_1",
        ownership_type="affiliate",
        platform="tiktok_shop",
        title="Producto demo",
        availability="available",
        affiliate_url="https://example.com/affiliate",
        price_amount=499,
        verified_benefits=["resuelve una necesidad concreta"],
        commercial_rights_status="approved",
        media_assets=["front.jpg", "side.jpg", "detail.jpg"],
    )


def profile() -> UGCProfile:
    return UGCProfile(brand_name="Cano Digital", cta="Revisa el precio actual")


def test_plan_is_dynamic_and_draft_only():
    plan = build_plan(product(), profile())
    assert len(plan.scenes) == 5
    assert plan.opportunity["score"] >= 75
    assert plan.creative_matrix["hooks"]
    assert plan.auto_publish is False
    assert plan.human_review_required is True
    assert plan.scope_id.startswith("scope_")


def test_plan_scope_is_stable():
    first = build_plan(product(), profile())
    second = build_plan(product(), profile())
    assert first.scope_id == second.scope_id


def test_missing_rights_fails_closed():
    blocked = product().model_copy(update={"commercial_rights_status": "pending"})
    try:
        build_plan(blocked, profile())
    except ValueError as error:
        assert "rights" in str(error)
    else:
        raise AssertionError("planning should fail without rights")


def test_unavailable_product_fails_closed():
    blocked = product().model_copy(update={"availability": "out_of_stock"})
    try:
        build_plan(blocked, profile())
    except ValueError as error:
        assert "available" in str(error)
    else:
        raise AssertionError("planning should fail for unavailable product")


def test_affiliate_plan_never_invents_personal_use_testimonial():
    plan = build_plan(product(), profile())
    text = " ".join(scene.natural_text.lower() for scene in plan.scenes)
    assert "lo probé" not in text
    assert "lo que más me gustó" not in text
    hooks = " ".join(plan.creative_matrix["hooks"]).lower()
    assert "lo probé" not in hooks
