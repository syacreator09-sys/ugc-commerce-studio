from ugc_commerce.confidence import assess_data_confidence
from ugc_commerce.offers import EvidenceValue, ProductOfferSnapshot


def offer(**updates):
    base=dict(platform="tiktok_shop", market="MX", product_id="p", title="Producto")
    base.update(updates)
    return ProductOfferSnapshot(**base)


def test_complete_verified_offer_has_high_confidence():
    report = assess_data_confidence(offer(
        price_amount=EvidenceValue.verified(499),
        currency=EvidenceValue.verified("MXN"),
        organic_commission_amount=EvidenceValue.verified(80),
        stock_status=EvidenceValue.verified("in_stock"),
        sales_count=EvidenceValue.verified(1200),
        review_count=EvidenceValue.verified(220),
        source_provenance=["product detail"],
    ))
    assert report.score >= 90
    assert report.missing_data == []


def test_sparse_invitation_is_low_confidence_and_lists_missing_data():
    report = assess_data_confidence(offer(
        displayed_earnings_amount=EvidenceValue.verified(181.90),
        displayed_earnings_currency=EvidenceValue.unknown(),
        shop_ads_commission_rate=EvidenceValue.verified(0.01),
        free_sample_available=EvidenceValue.verified(True),
        source_provenance=["screenshot"],
    ))
    assert report.score < 60
    assert "currency" in report.missing_data
    assert "price" in report.missing_data
    assert "organic_commission" in report.missing_data
    assert "stock" in report.missing_data
    assert "demand" in report.missing_data


def test_inferred_critical_values_are_penalized_vs_verified():
    verified = assess_data_confidence(offer(
        price_amount=EvidenceValue.verified(500), currency=EvidenceValue.verified("MXN"),
        organic_commission_amount=EvidenceValue.verified(80), stock_status=EvidenceValue.verified("in_stock"),
        sales_count=EvidenceValue.verified(100), review_count=EvidenceValue.verified(20), source_provenance=["page"],
    ))
    inferred = assess_data_confidence(offer(
        price_amount=EvidenceValue.inferred(500), currency=EvidenceValue.inferred("MXN"),
        organic_commission_amount=EvidenceValue.inferred(80), stock_status=EvidenceValue.inferred("in_stock"),
        sales_count=EvidenceValue.inferred(100), review_count=EvidenceValue.inferred(20), source_provenance=["model inference"],
    ))
    assert inferred.score < verified.score


def test_critical_evidence_conflict_is_large_penalty():
    report = assess_data_confidence(offer(
        price_amount=EvidenceValue.verified(500), currency=EvidenceValue.verified("MXN"),
        organic_commission_amount=EvidenceValue.verified(80), stock_status=EvidenceValue.verified("in_stock"),
        sales_count=EvidenceValue.verified(100), review_count=EvidenceValue.verified(20), source_provenance=["page"],
        critical_evidence_conflict=True,
    ))
    assert report.score <= 70
    assert "critical_evidence_conflict" in report.deductions


def test_stale_verified_offer_is_penalized():
    from datetime import datetime, timedelta, timezone
    current = datetime(2026, 8, 14, tzinfo=timezone.utc)
    stale = offer(
        price_amount=EvidenceValue.verified(499),
        currency=EvidenceValue.verified("MXN"),
        organic_commission_amount=EvidenceValue.verified(80),
        stock_status=EvidenceValue.verified("in_stock"),
        sales_count=EvidenceValue.verified(1200),
        review_count=EvidenceValue.verified(220),
        source_provenance=["product detail"],
        verified_at=current - timedelta(days=30),
    )
    report = assess_data_confidence(stale, now=current, max_age_days=7)
    assert "stale_offer_evidence" in report.deductions
    assert report.score < 100
