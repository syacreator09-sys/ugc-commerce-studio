import json

from ugc_commerce.domain import Approval, ProductManifest, UGCProfile
from ugc_commerce.higgsfield import HiggsfieldClient
from ugc_commerce.planner import build_plan


def product():
    return ProductManifest(
        product_id="p",
        ownership_type="affiliate",
        platform="tiktok_shop",
        title="Producto",
        source_url="https://example.com/p",
        affiliate_url="https://example.com/a",
        availability="available",
        price_amount=1,
        verified_benefits=["beneficio"],
        media_assets=["front.jpg", "side.jpg", "detail.jpg"],
        commercial_rights_status="approved",
    )


def test_direct_scene_uses_start_image():
    plan = build_plan(product(), UGCProfile(brand_name="Cano", cta="Compra"), workflow="direct_scene")
    command = HiggsfieldClient(enabled=True)._command_for_scene(plan, plan.scenes[0], product_id=None)
    assert "--start-image" in command
    assert "kling3_0" in command


def test_marketing_studio_passes_product_and_avatar():
    profile = UGCProfile(brand_name="Cano", cta="Compra", avatar_id="avatar-1", avatar_type="custom")
    plan = build_plan(product(), profile)
    command = HiggsfieldClient(enabled=True)._command_for_scene(plan, plan.scenes[0], product_id="product-1")
    assert "marketing_studio_video" in command
    assert "--product_ids" in command
    assert "--avatars" in command
    assert "--generate_audio" in command

    product_file = command[command.index("--product_ids") + 1][1:]
    avatar_file = command[command.index("--avatars") + 1][1:]
    with open(product_file, encoding="utf-8") as handle:
        assert json.load(handle) == ["product-1"]
    with open(avatar_file, encoding="utf-8") as handle:
        assert json.load(handle) == [{"id": "avatar-1", "type": "custom"}]


def test_scope_mismatch_is_blocked(tmp_path):
    plan = build_plan(product(), UGCProfile(brand_name="Cano", cta="Compra"))
    approval = Approval(scope_id="wrong", approved_by="tester")
    try:
        HiggsfieldClient(enabled=True).execute_plan(plan, approval, tmp_path)
    except Exception as error:
        assert "scope" in str(error)
    else:
        raise AssertionError("mismatched approval must be blocked")
