from ugc_commerce.economics import EconomicsScenario, ProductionCosts, calculate_affiliate_economics
from ugc_commerce.offers import EvidenceValue, ProductOfferSnapshot


def offer(**updates):
    base = dict(platform="tiktok_shop", market="MX", product_id="p1", title="Producto")
    base.update(updates)
    return ProductOfferSnapshot(**base)


def test_organic_commission_prefers_verified_amount():
    result = calculate_affiliate_economics(offer(
        price_amount=EvidenceValue.verified(1000),
        organic_commission_rate=EvidenceValue.verified(0.10),
        organic_commission_amount=EvidenceValue.verified(125),
        currency=EvidenceValue.verified("MXN"),
    ))
    assert result.organic_commission_per_sale == 125


def test_organic_commission_can_be_rate_times_verified_price():
    result = calculate_affiliate_economics(offer(
        price_amount=EvidenceValue.verified(800),
        organic_commission_rate=EvidenceValue.verified(0.10),
        currency=EvidenceValue.verified("MXN"),
    ))
    assert result.organic_commission_per_sale == 80


def test_shop_ads_is_separate_from_organic_commission():
    result = calculate_affiliate_economics(offer(
        price_amount=EvidenceValue.verified(1000),
        currency=EvidenceValue.verified("MXN"),
        organic_commission_rate=EvidenceValue.verified(0.12),
        shop_ads_commission_rate=EvidenceValue.verified(0.01),
    ))
    assert result.organic_commission_per_sale == 120
    assert result.shop_ads_commission_per_sale == 10


def test_unknown_price_blocks_rate_based_commission():
    result = calculate_affiliate_economics(offer(
        organic_commission_rate=EvidenceValue.verified(0.10),
        shop_ads_commission_rate=EvidenceValue.verified(0.01),
    ))
    assert result.organic_commission_per_sale is None
    assert result.shop_ads_commission_per_sale is None
    assert "price" in result.missing_data


def test_displayed_earnings_without_currency_is_not_treated_as_commission():
    result = calculate_affiliate_economics(offer(
        displayed_earnings_amount=EvidenceValue.verified(181.90, source="screenshot"),
        displayed_earnings_currency=EvidenceValue.unknown(source="screenshot"),
        shop_ads_commission_rate=EvidenceValue.verified(0.01, source="screenshot"),
        free_sample_available=EvidenceValue.verified(True, source="screenshot"),
    ))
    assert result.organic_commission_per_sale is None
    assert result.shop_ads_commission_per_sale is None
    assert "currency" in result.missing_data
    assert "organic_commission" in result.missing_data


def test_projection_uses_decimal_ctr_and_cvr_and_exposes_per_video_values():
    result = calculate_affiliate_economics(
        offer(
            organic_commission_amount=EvidenceValue.verified(100),
            currency=EvidenceValue.verified("MXN"),
            source_provenance=["affiliate detail"],
        ),
        scenarios=[EconomicsScenario(name="base", views=1000, ctr=0.02, cvr=0.05)],
    )
    p = result.scenarios[0]
    assert p.clicks == 20
    assert p.orders == 1
    assert p.expected_orders_per_1000_views == 1
    assert p.organic_revenue == 100
    assert p.expected_organic_commission_per_video == 100
    assert p.organic_commission_per_1000_views == 100
    assert result.source_provenance == ["affiliate detail"]


def test_break_even_uses_all_optional_test_costs_including_flat_production_cost():
    result = calculate_affiliate_economics(
        offer(organic_commission_amount=EvidenceValue.verified(80), currency=EvidenceValue.verified("MXN")),
        costs=ProductionCosts(
            production_cost_mxn=30,
            sample_cost_mxn=0,
            generation_cost_mxn=100,
            editing_cost_mxn=20,
            other_cost_mxn=5,
        ),
    )
    assert result.total_test_cost_mxn == 155
    assert result.orders_to_break_even == 2


def test_zero_or_unknown_commission_never_divides_by_zero():
    zero = calculate_affiliate_economics(offer(organic_commission_amount=EvidenceValue.verified(0)))
    unknown = calculate_affiliate_economics(offer())
    assert zero.orders_to_break_even is None
    assert unknown.orders_to_break_even is None


def test_break_even_requires_matching_commission_and_cost_currency():
    result = calculate_affiliate_economics(
        offer(
            organic_commission_amount=EvidenceValue.verified(20),
            currency=EvidenceValue.verified("USD"),
        ),
        costs=ProductionCosts(generation_cost_mxn=100),
    )
    assert result.orders_to_break_even is None
    assert "break_even_currency_mismatch" in result.missing_data
