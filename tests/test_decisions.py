from ugc_commerce.confidence import assess_data_confidence
from ugc_commerce.creative_capacity import CreativeCapacityInput, assess_creative_capacity
from ugc_commerce.decisions import ProductionDecision, SampleDecision, decide_product
from ugc_commerce.economics import calculate_affiliate_economics
from ugc_commerce.offers import EvidenceValue, ProductOfferSnapshot
from ugc_commerce.product_scout_score import ChannelFitTier, ProductScoutInput, score_product


def offer(**updates):
    base=dict(platform="tiktok_shop", market="MX", product_id="p", title="Producto", source_provenance=["page"])
    base.update(updates)
    return ProductOfferSnapshot(**base)


def strong_scout(**updates):
    base=dict(commission_mxn=160, understandable_in_3s=True, has_clear_visual_change=True, is_photogenic=True,
              channel_fit=ChannelFitTier.PERFECT, solves_specific_common_pain=True, is_impulse_priced=True,
              is_trending=True, has_good_url_images=True, no_real_action_video_required=True, simple_avatar_and_script=True)
    base.update(updates)
    return score_product(ProductScoutInput(**base))


def complete_offer(**updates):
    base=dict(
        price_amount=EvidenceValue.verified(499), currency=EvidenceValue.verified("MXN"),
        organic_commission_amount=EvidenceValue.verified(80), stock_status=EvidenceValue.verified("in_stock"),
        sales_count=EvidenceValue.verified(1000), review_count=EvidenceValue.verified(200),
        free_sample_available=EvidenceValue.verified(True), commercial_rights_status="approved",
    )
    base.update(updates)
    return offer(**base)


def decide(o, scout=None):
    scout = scout or strong_scout()
    return decide_product(
        offer=o,
        economics=calculate_affiliate_economics(o),
        confidence=assess_data_confidence(o),
        ugc_score=scout,
        creative_capacity=assess_creative_capacity(CreativeCapacityInput(hooks=["h1","h2","h3"], formats=["pov","review","demo"])),
    )


def test_free_sample_with_missing_economics_returns_needs_data():
    o = offer(free_sample_available=EvidenceValue.verified(True), displayed_earnings_amount=EvidenceValue.verified(181.90), shop_ads_commission_rate=EvidenceValue.verified(0.01))
    result = decide(o)
    assert result.sample_decision == SampleDecision.NEEDS_DATA
    assert result.production_decision == ProductionDecision.EN_ESPERA


def test_strong_verified_candidate_requests_sample_and_proceeds():
    result = decide(complete_offer())
    assert result.sample_decision == SampleDecision.SOLICITAR
    assert result.production_decision == ProductionDecision.PROCEDE


def test_medical_claim_hard_gate_cannot_be_overridden_by_high_commission():
    o = complete_offer(requires_medical_claims=True)
    result = decide(o, strong_scout(requires_medical_claims=True))
    assert result.sample_decision == SampleDecision.NO_SOLICITAR
    assert result.production_decision == ProductionDecision.RECHAZADO
    assert any("medical" in reason.lower() for reason in result.hard_gates)


def test_rejected_commercial_rights_is_hard_reject():
    result = decide(complete_offer(commercial_rights_status="rejected"))
    assert result.sample_decision == SampleDecision.NO_SOLICITAR
    assert result.production_decision == ProductionDecision.RECHAZADO


def test_low_confidence_waits_even_with_high_ugc_score():
    o = offer(price_amount=EvidenceValue.verified(499), organic_commission_amount=EvidenceValue.verified(180), free_sample_available=EvidenceValue.verified(True))
    result = decide(o)
    assert result.production_decision == ProductionDecision.EN_ESPERA


def test_known_nonblocking_platform_restriction_is_risk_not_hard_gate():
    o = complete_offer(has_known_platform_restrictions=True)
    result = decide(o)
    assert result.production_decision == ProductionDecision.PROCEDE
    assert not result.hard_gates


def test_blocking_platform_restriction_is_hard_reject():
    o = complete_offer(has_blocking_platform_restrictions=True)
    result = decide(o)
    assert result.production_decision == ProductionDecision.RECHAZADO
    assert any("platform" in reason.lower() for reason in result.hard_gates)
