from ugc_commerce.domain import ProductManifest
from ugc_commerce.offers import EvidenceStatus, EvidenceValue, ProductOfferSnapshot


def test_sparse_invitation_keeps_displayed_currency_unknown():
    offer = ProductOfferSnapshot(
        platform="tiktok_shop",
        market="MX",
        product_id="inv-1",
        title="Flexible LED Display",
        displayed_earnings_amount=EvidenceValue.verified(181.90, source="screenshot"),
        displayed_earnings_currency=EvidenceValue.unknown(source="screenshot"),
        shop_ads_commission_rate=EvidenceValue.verified(0.01, source="screenshot"),
        free_sample_available=EvidenceValue.verified(True, source="screenshot"),
    )
    assert offer.displayed_earnings_amount.value == 181.90
    assert offer.displayed_earnings_currency.value is None
    assert offer.displayed_earnings_currency.status == EvidenceStatus.UNKNOWN
    assert offer.price_amount.status == EvidenceStatus.UNKNOWN


def test_evidence_value_helpers_preserve_provenance():
    value = EvidenceValue.estimated(0.02, source="historical baseline")
    assert value.status == EvidenceStatus.ESTIMATED
    assert value.source == "historical baseline"


def test_product_manifest_conversion_is_backwards_compatible():
    manifest = ProductManifest(
        product_id="p1",
        ownership_type="affiliate",
        platform="tiktok_shop",
        title="Producto",
        source_url="https://example.com/p",
        affiliate_url="https://example.com/a",
        price_amount=499,
        currency="MXN",
        availability="available",
        commission_value=80,
        verified_benefits=["beneficio"],
        commercial_rights_status="approved",
    )
    offer = ProductOfferSnapshot.from_manifest(manifest)
    assert offer.product_id == "p1"
    assert offer.price_amount.value == 499
    assert offer.price_amount.status == EvidenceStatus.INFERRED
    assert offer.currency.value == "MXN"
    assert offer.currency.status == EvidenceStatus.INFERRED
    assert offer.organic_commission_amount.value == 80
    assert offer.organic_commission_amount.status == EvidenceStatus.INFERRED
    assert offer.commercial_rights_status == "approved"
