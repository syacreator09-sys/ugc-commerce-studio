"""One-scene pilot always has its own approval scope, never auto-runs."""
import pytest
from ugc_commerce.domain import ProductManifest, Scene, UGCPlan, UGCProfile
from scripts.build_one_scene_pilot import make_pilot


def parent_plan(approved=True):
    prod = ProductManifest(
        product_id="id-p", ownership_type="owned", platform="own_store",
        title="Real product", availability="available", price_amount=100,
        verified_benefits=["holds stationery"],
        media_assets=["approved.png"], commercial_rights_status="approved" if approved else "pending",
    )
    profile = UGCProfile(brand_name="Brand", cta="Learn more")
    scenes = [Scene(
        index=i, goal="beat", natural_text="Real approved script",
        spoken_text="Real approved script", caption_text="Real approved script",
        vibe="natural", visual_direction="product", duration_seconds=5,
    ) for i in range(1, 7)]
    return UGCPlan.create(workflow="direct_scene", mode="ugc", model="kling3_0",
                          product=prod, profile=profile, opportunity={},
                          creative_matrix={}, scenes=scenes)


def test_pilot_does_not_inherit_parent_approval():
    parent = parent_plan()
    child = make_pilot(parent, 3)
    assert child.scope_id != parent.scope_id
    assert len(child.scenes) == 1
    assert child.scenes[0].index == 1
    assert child.creative_matrix["pilot_from_six_scene_plan"]["source_scene_index"] == 3
    assert child.creative_matrix["pilot_from_six_scene_plan"]["parent_scope_id"] == parent.scope_id
    assert child.auto_publish is False


def test_rejected_rights_block_pilot():
    with pytest.raises(ValueError, match="rights"):
        make_pilot(parent_plan(approved=False))


def test_invalid_scene_index_blocked():
    with pytest.raises(ValueError, match="index"):
        make_pilot(parent_plan(), 7)
