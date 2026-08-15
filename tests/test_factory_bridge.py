import pytest

from ugc_commerce.creative_capacity import CreativeCapacityInput
from ugc_commerce.economics import EconomicsScenario, ProductionCosts
from ugc_commerce.factory_bridge import (
    CommerceOrderStatus,
    FactoryProductionReceiptV1,
    approve_factory_order,
    build_factory_order,
    validate_factory_receipt,
    verify_order_scope,
)
from ugc_commerce.offers import EvidenceValue, ProductOfferSnapshot
from ugc_commerce.product_intelligence import analyze_product_offer
from ugc_commerce.product_scout_score import ProductScoutInput
from ugc_commerce.production_economics import (
    CostBenefitRecommendation,
    ProductionEconomicsInput,
    analyze_production_cost_benefit,
)


def strong_offer(currency="MXN"):
    return ProductOfferSnapshot(
        platform="tiktok_shop",
        market="MX",
        seller_name="Seller",
        product_id="led-1",
        title="Flexible LED",
        source_url="https://example.com/led",
        price_amount=EvidenceValue.verified(899, source="fixture"),
        currency=EvidenceValue.verified(currency, source="fixture"),
        organic_commission_amount=EvidenceValue.verified(181.90, source="fixture"),
        shop_ads_commission_rate=EvidenceValue.verified(0.01, source="fixture"),
        free_sample_available=EvidenceValue.verified(True, source="fixture"),
        sales_count=EvidenceValue.verified(1000, source="fixture"),
        review_count=EvidenceValue.verified(100, source="fixture"),
        stock_status=EvidenceValue.verified("in_stock", source="fixture"),
        commercial_rights_status="approved",
        media_assets=["front.jpg", "demo.jpg"],
        verified_benefits=["flexible LED display"],
        prohibited_claims=["guaranteed sales"],
        source_provenance=["fixture"],
    )


def scout_input():
    return ProductScoutInput(
        commission_mxn=181.9,
        understandable_in_3s=True,
        has_clear_visual_change=True,
        is_photogenic=True,
        channel_fit="perfect",
        solves_specific_common_pain=True,
        is_impulse_priced=True,
        is_trending=True,
        has_good_url_images=True,
        no_real_action_video_required=True,
        simple_avatar_and_script=True,
    )


def creative_input():
    return CreativeCapacityInput(
        hooks=["transform", "curiosity", "problem", "pov"],
        audiences=["shops", "creators"],
        use_cases=["store", "desk", "event"],
        demonstrations=["bend", "text", "color"],
        objections=["setup", "visibility"],
        transformations=["off-on", "blank-message"],
        formats=["demo", "review", "pov", "problem-solution", "tutorial"],
    )


def economics_input(cost=200, currency="MXN"):
    return ProductionEconomicsInput(
        costs=ProductionCosts(currency=currency, generation_cost_mxn=cost),
        scenarios=[
            EconomicsScenario(name="conservative", views=1000, ctr=0.01, cvr=0.03),
            EconomicsScenario(name="base", views=5000, ctr=0.02, cvr=0.05),
            EconomicsScenario(name="aggressive", views=10000, ctr=0.03, cvr=0.06),
        ],
    )


def test_positive_base_economics_requires_human_approval():
    result = analyze_production_cost_benefit(strong_offer(), economics_input(cost=200))
    assert result.recommendation == CostBenefitRecommendation.APPROVAL_REQUIRED
    assert result.base_expected_commission == pytest.approx(909.5)
    assert result.base_net_benefit == pytest.approx(709.5)
    assert result.base_roi == pytest.approx(3.5475)
    assert result.projections[1].break_even_views == pytest.approx(1099.5052, rel=1e-4)


def test_negative_base_economics_is_not_economic():
    result = analyze_production_cost_benefit(strong_offer(), economics_input(cost=1200))
    assert result.recommendation == CostBenefitRecommendation.NOT_ECONOMIC
    assert result.base_net_benefit < 0


def test_unknown_or_mismatched_currency_never_gets_approval_recommendation():
    unknown = strong_offer()
    unknown.currency = EvidenceValue.unknown(source="fixture")
    assert analyze_production_cost_benefit(unknown, economics_input()).recommendation == CostBenefitRecommendation.NEEDS_DATA
    assert analyze_production_cost_benefit(strong_offer("USD"), economics_input()).recommendation == CostBenefitRecommendation.NEEDS_DATA


def test_order_is_ready_for_approval_and_scope_is_immutable():
    offer = strong_offer()
    intelligence = analyze_product_offer(offer, scout_input(), creative_input())
    benefit = analyze_production_cost_benefit(offer, economics_input())
    order = build_factory_order(
        offer=offer,
        intelligence=intelligence,
        economics=benefit,
        target_channel="cano",
        angles=["transform", "curiosity", "problem", "pov", "demo"],
        creative_count=3,
    )
    assert order.status == CommerceOrderStatus.READY_FOR_APPROVAL
    assert verify_order_scope(order)
    assert order.creative_count == 3
    assert order.economics.base_net_benefit > 0

    tampered = order.model_copy(update={"target_channel": "cass"})
    assert not verify_order_scope(tampered)
    with pytest.raises(ValueError, match="scope"):
        approve_factory_order(tampered, approved_by="cano")


def test_explicit_human_approval_transitions_order_without_changing_scope():
    offer = strong_offer()
    intelligence = analyze_product_offer(offer, scout_input(), creative_input())
    benefit = analyze_production_cost_benefit(offer, economics_input())
    order = build_factory_order(
        offer=offer,
        intelligence=intelligence,
        economics=benefit,
        target_channel="cano",
        angles=["transform", "curiosity", "problem"],
        creative_count=3,
    )
    approved = approve_factory_order(order, approved_by="cano")
    assert approved.status == CommerceOrderStatus.APPROVED
    assert approved.approved_by == "cano"
    assert approved.approved_at is not None
    assert approved.scope_id == order.scope_id
    assert verify_order_scope(approved)


def test_non_proceed_product_cannot_create_factory_order():
    offer = strong_offer()
    offer.requires_medical_claims = True
    intelligence = analyze_product_offer(offer, scout_input(), creative_input())
    benefit = analyze_production_cost_benefit(offer, economics_input())
    with pytest.raises(ValueError, match="not approved production"):
        build_factory_order(
            offer=offer,
            intelligence=intelligence,
            economics=benefit,
            target_channel="cano",
            angles=["a"],
            creative_count=1,
        )


def test_factory_receipt_must_correlate_to_order():
    offer = strong_offer()
    intelligence = analyze_product_offer(offer, scout_input(), creative_input())
    benefit = analyze_production_cost_benefit(offer, economics_input())
    order = approve_factory_order(build_factory_order(
        offer=offer,
        intelligence=intelligence,
        economics=benefit,
        target_channel="cano",
        angles=["transform", "curiosity", "problem"],
        creative_count=3,
    ), approved_by="cano")
    receipt = FactoryProductionReceiptV1(
        order_id=order.order_id,
        scope_id=order.scope_id,
        status="QUEUED",
        production_job_ids=[1, 2, 3],
    )
    validate_factory_receipt(order, receipt)
    bad = receipt.model_copy(update={"scope_id": "wrong"})
    with pytest.raises(ValueError, match="correlate"):
        validate_factory_receipt(order, bad)
