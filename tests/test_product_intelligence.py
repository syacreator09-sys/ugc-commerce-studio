from ugc_commerce.creative_capacity import CreativeCapacityInput
from ugc_commerce.decisions import ProductionDecision, SampleDecision
from ugc_commerce.economics import EconomicsScenario
from ugc_commerce.offers import EvidenceValue, ProductOfferSnapshot
from ugc_commerce.product_intelligence import analyze_product_offer
from ugc_commerce.product_scout_score import ChannelFitTier, ProductScoutInput


def scout(**updates):
    base=dict(commission_mxn=160, understandable_in_3s=True, has_clear_visual_change=True, is_photogenic=True,
              channel_fit=ChannelFitTier.PERFECT, solves_specific_common_pain=True, is_impulse_priced=True,
              is_trending=True, has_good_url_images=True, no_real_action_video_required=True, simple_avatar_and_script=True)
    base.update(updates)
    return ProductScoutInput(**base)


def creative():
    return CreativeCapacityInput(
        hooks=["h1","h2","h3","h4"], audiences=["a1","a2"], use_cases=["u1","u2"],
        demonstrations=["d1","d2"], objections=["o1"], transformations=["t1"],
        formats=["review","pov","tutorial","problem-solution"],
    )


def strong_offer(**updates):
    base=dict(platform="tiktok_shop", market="MX", product_id="p", title="LED",
        price_amount=EvidenceValue.verified(899), currency=EvidenceValue.verified("MXN"),
        organic_commission_amount=EvidenceValue.verified(181.9), shop_ads_commission_rate=EvidenceValue.verified(0.01),
        free_sample_available=EvidenceValue.verified(True), stock_status=EvidenceValue.verified("in_stock"),
        sales_count=EvidenceValue.verified(2500), review_count=EvidenceValue.verified(450), rating=EvidenceValue.verified(4.7),
        source_provenance=["product page"], commercial_rights_status="approved")
    base.update(updates)
    return ProductOfferSnapshot(**base)


def test_complete_product_intelligence_report_proceeds():
    report = analyze_product_offer(
        strong_offer(), scout(), creative(),
        scenarios=[EconomicsScenario(name="base", views=1000, ctr=0.02, cvr=0.05)],
    )
    assert report.data_quality.score >= 90
    assert report.economics.organic_commission_per_sale == 181.9
    assert report.ugc_fit_raw_score == 90
    assert report.ugc_fit_normalized_score == 100
    assert report.sample_decision == SampleDecision.SOLICITAR
    assert report.production_decision == ProductionDecision.PROCEDE
    assert report.recommended_initial_creatives == 5


def test_sparse_invitation_report_keeps_181_90_currency_unknown():
    offer = ProductOfferSnapshot(
        platform="tiktok_shop", market="MX", product_id="inv", title="Flexible LED",
        displayed_earnings_amount=EvidenceValue.verified(181.90, source="screenshot"),
        displayed_earnings_currency=EvidenceValue.unknown(source="screenshot"),
        shop_ads_commission_rate=EvidenceValue.verified(0.01, source="screenshot"),
        free_sample_available=EvidenceValue.verified(True, source="screenshot"),
        source_provenance=["screenshot"], commercial_rights_status="pending",
    )
    report = analyze_product_offer(offer, scout(commission_mxn=None), creative())
    assert report.ugc_score.commission_points == 0
    assert report.economics.currency is None
    assert report.economics.organic_commission_per_sale is None
    assert report.economics.shop_ads_commission_per_sale is None
    assert report.sample_decision == SampleDecision.NEEDS_DATA
    assert report.production_decision == ProductionDecision.EN_ESPERA
    assert {"currency","price","organic_commission"}.issubset(set(report.missing_data))


def test_medical_hard_gate_rejects_even_with_strong_economics():
    report = analyze_product_offer(strong_offer(requires_medical_claims=True), scout(requires_medical_claims=True), creative())
    assert report.production_decision == ProductionDecision.RECHAZADO
    assert report.sample_decision == SampleDecision.NO_SOLICITAR
    assert report.risk
