from datetime import datetime, timezone

import pytest

from ugc_commerce.creative_capacity import CreativeCapacityInput
from ugc_commerce.economics import EconomicsScenario, ProductionCosts
from ugc_commerce.factory_bridge import CommerceCreativeTrace, build_factory_order, verify_order_scope
from ugc_commerce.offers import EvidenceValue, ProductOfferSnapshot
from ugc_commerce.priors import CommercePerformancePriorV1
from ugc_commerce.product_intelligence import analyze_product_offer
from ugc_commerce.product_scout_score import ProductScoutInput
from ugc_commerce.production_economics import ProductionEconomicsInput, analyze_production_cost_benefit
from ugc_commerce.review_evidence import CommerceReviewEvidenceV1, derive_review_creative_signals


def _offer():
    return ProductOfferSnapshot(
        platform="tiktok_shop",
        market="MX",
        seller_name="Seller",
        product_id="led-1",
        title="Flexible LED",
        source_url="https://example.com/led",
        price_amount=EvidenceValue.verified(899, source="fixture"),
        currency=EvidenceValue.verified("MXN", source="fixture"),
        organic_commission_amount=EvidenceValue.verified(181.90, source="fixture"),
        free_sample_available=EvidenceValue.verified(True, source="fixture"),
        sales_count=EvidenceValue.verified(1000, source="fixture"),
        review_count=EvidenceValue.verified(100, source="fixture"),
        stock_status=EvidenceValue.verified("in_stock", source="fixture"),
        commercial_rights_status="approved",
        media_assets=["front.jpg"],
        verified_benefits=["flexible LED display"],
        source_provenance=["fixture"],
    )


def _prior(classification="PROMISING", sample_size=8, confidence=67):
    return CommercePerformancePriorV1(
        prior_id="mio-prior-0123456789abcdef0123",
        platform="tiktok",
        window_hours=72,
        filters={"hook_family": "problem-solution"},
        sample_size=sample_size,
        ctr_median=0.02,
        cvr_median=0.05,
        ctr_stdev=0.005,
        cvr_stdev=0.01,
        classification=classification,
        confidence_score=confidence,
        source_refs=["mio:metrics-72h"],
        causal_claim=False,
        generated_at=datetime.now(timezone.utc),
    )


def test_compatible_mio_prior_fills_base_scenario():
    result = analyze_production_cost_benefit(
        _offer(),
        ProductionEconomicsInput(
            costs=ProductionCosts(currency="MXN", generation_cost_mxn=200),
            historical_prior=_prior(),
            prior_context={"hook_family": "problem-solution"},
        ),
    )
    assert result.historical_prior_applied is True
    assert result.base_scenario == "base"
    base = next(p for p in result.projections if p.name == "base")
    assert base.ctr == pytest.approx(0.02)
    assert base.cvr == pytest.approx(0.05)
    assert result.historical_prior_source_refs == ["mio:metrics-72h"]


def test_segmented_prior_is_ignored_when_creative_context_does_not_match():
    result = analyze_production_cost_benefit(
        _offer(),
        ProductionEconomicsInput(
            costs=ProductionCosts(currency="MXN"),
            historical_prior=_prior(),
            prior_context={"hook_family": "curiosity"},
        ),
    )
    assert result.historical_prior_applied is False
    assert result.base_scenario is None
    assert result.recommendation == "NEEDS_DATA"
    assert any("filter context mismatch" in note for note in result.assumptions)


def test_segmented_prior_is_ignored_when_required_context_is_missing():
    result = analyze_production_cost_benefit(
        _offer(),
        ProductionEconomicsInput(
            costs=ProductionCosts(currency="MXN"),
            historical_prior=_prior(),
        ),
    )
    assert result.historical_prior_applied is False
    assert any("hook_family=<missing>" in note for note in result.assumptions)


def test_inconclusive_prior_is_not_silently_used():
    result = analyze_production_cost_benefit(
        _offer(),
        ProductionEconomicsInput(
            costs=ProductionCosts(currency="MXN"),
            historical_prior=_prior(classification="INCONCLUSIVE", sample_size=3, confidence=24),
            prior_context={"hook_family": "problem-solution"},
        ),
    )
    assert result.historical_prior_applied is False
    assert result.base_scenario is None
    assert result.recommendation == "NEEDS_DATA"
    assert "base_scenario" in result.missing_data


def test_explicit_scenarios_override_historical_prior():
    result = analyze_production_cost_benefit(
        _offer(),
        ProductionEconomicsInput(
            historical_prior=_prior(),
            scenarios=[EconomicsScenario(name="base", views=1000, ctr=0.10, cvr=0.20)],
        ),
    )
    assert result.historical_prior_applied is False
    assert result.projections[0].ctr == pytest.approx(0.10)
    assert any("override historical prior" in note for note in result.assumptions)


def test_review_evidence_creates_angles_not_verified_claims():
    offer = _offer()
    before = list(offer.verified_benefits)
    evidence = CommerceReviewEvidenceV1(
        evidence_id="review-digest:led-1",
        product_ref="led-1",
        sample_size=20,
        average_rating=4.4,
        recurring_complaints=["setup is confusing"],
        unmet_needs=["clearer install guide"],
        quality_expectations=["bright readable display"],
        source_refs=["reviews:dataset-1"],
        provenance=["product-ip-factory:ReviewDigest"],
        generated_at=datetime.now(timezone.utc),
    )
    signals = derive_review_creative_signals(evidence)
    assert "complaint:setup is confusing" in signals.angle_candidates
    assert "unmet_need:clearer install guide" in signals.angle_candidates
    assert offer.verified_benefits == before
    assert not hasattr(evidence, "verified_claims")


def _intelligence(offer):
    scout = ProductScoutInput(
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
    creative = CreativeCapacityInput(
        hooks=["problem", "demo", "curiosity"],
        audiences=["shops"],
        use_cases=["store"],
        demonstrations=["bend", "display"],
        objections=["setup"],
        transformations=["off-on"],
        formats=["demo", "problem-solution", "review"],
    )
    return analyze_product_offer(offer, scout, creative)


def test_mio_trace_is_part_of_immutable_approval_scope():
    offer = _offer()
    intelligence = _intelligence(offer)
    benefit = analyze_production_cost_benefit(
        offer,
        ProductionEconomicsInput(
            scenarios=[EconomicsScenario(name="base", views=5000, ctr=0.02, cvr=0.05)]
        ),
    )
    a = build_factory_order(
        offer=offer,
        intelligence=intelligence,
        economics=benefit,
        target_channel="cano",
        angles=["problem", "demo"],
        creative_count=2,
        creative_trace=CommerceCreativeTrace(
            mio_brief_id="brief-1",
            experiment_id="exp-1",
            variant_id="var-a",
            hook_family="problem-solution",
            evidence_refs=["mio:brief-1", "review-digest:led-1"],
        ),
    )
    b = build_factory_order(
        offer=offer,
        intelligence=intelligence,
        economics=benefit,
        target_channel="cano",
        angles=["problem", "demo"],
        creative_count=2,
        creative_trace=CommerceCreativeTrace(
            mio_brief_id="brief-1",
            experiment_id="exp-1",
            variant_id="var-b",
            hook_family="curiosity",
            evidence_refs=["mio:brief-1", "review-digest:led-1"],
        ),
    )
    assert verify_order_scope(a) and verify_order_scope(b)
    assert a.scope_id != b.scope_id
    assert a.order_id != b.order_id
