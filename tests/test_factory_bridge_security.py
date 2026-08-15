import pytest

from ugc_commerce.creative_capacity import CreativeCapacityInput
from ugc_commerce.economics import EconomicsScenario, ProductionCosts
from ugc_commerce.factory_bridge import approve_factory_order, build_factory_order, verify_order_scope
from ugc_commerce.offers import EvidenceValue, ProductOfferSnapshot
from ugc_commerce.product_intelligence import analyze_product_offer
from ugc_commerce.product_scout_score import ProductScoutInput
from ugc_commerce.production_economics import ProductionEconomicsInput, analyze_production_cost_benefit


def approved_candidate():
    offer = ProductOfferSnapshot(
        platform="tiktok_shop", market="MX", product_id="p-sec", title="Product",
        price_amount=EvidenceValue.verified(899, source="test"),
        currency=EvidenceValue.verified("MXN", source="test"),
        organic_commission_amount=EvidenceValue.verified(181.9, source="test"),
        free_sample_available=EvidenceValue.verified(True, source="test"),
        stock_status=EvidenceValue.verified("in_stock", source="test"),
        sales_count=EvidenceValue.verified(1000, source="test"),
        review_count=EvidenceValue.verified(100, source="test"),
        commercial_rights_status="approved", source_provenance=["test"],
    )
    scout = ProductScoutInput(
        commission_mxn=181.9, understandable_in_3s=True, has_clear_visual_change=True,
        is_photogenic=True, channel_fit="perfect", solves_specific_common_pain=True,
        is_impulse_priced=True, is_trending=True, has_good_url_images=True,
        no_real_action_video_required=True, simple_avatar_and_script=True,
    )
    creative = CreativeCapacityInput(
        hooks=["a","b","c"], audiences=["x"], use_cases=["u"], demonstrations=["d"],
        transformations=["t"], formats=["demo","review","pov"],
    )
    intelligence = analyze_product_offer(offer, scout, creative)
    benefit = analyze_production_cost_benefit(offer, ProductionEconomicsInput(
        costs=ProductionCosts(currency="MXN", generation_cost_mxn=100),
        scenarios=[EconomicsScenario(name="base", views=5000, ctr=0.02, cvr=0.05)],
    ))
    return build_factory_order(
        offer=offer, intelligence=intelligence, economics=benefit, target_channel="cano",
        angles=["demo","review","pov"], creative_count=3,
    )


def test_order_id_is_bound_to_scope():
    order = approved_candidate()
    assert verify_order_scope(order)
    assert not verify_order_scope(order.model_copy(update={"order_id": "cpo-00000000000000000000"}))


def test_agent_names_cannot_self_approve_factory_order():
    order = approved_candidate()
    for actor in ("system", "agent", "claude", "codex", "automation"):
        with pytest.raises(ValueError, match="human"):
            approve_factory_order(order, approved_by=actor)
