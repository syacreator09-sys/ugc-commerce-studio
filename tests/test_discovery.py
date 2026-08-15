from ugc_commerce.discovery.manual import ManualDiscoveryProvider
from ugc_commerce.offers import EvidenceStatus
from ugc_commerce.providers.tiktok_shop.invitation import normalize_tiktok_invitation


def test_manual_discovery_normalizes_structured_offer_without_network():
    provider = ManualDiscoveryProvider()
    candidates = provider.discover([{
        "platform": "tiktok_shop", "market": "MX", "product_id": "p1", "title": "LED",
        "price_amount": 899, "currency": "MXN", "organic_commission_amount": 181.9,
        "source": "manual-test",
    }])
    assert len(candidates) == 1
    offer = candidates[0].offer
    assert offer.price_amount.value == 899
    assert offer.price_amount.status == EvidenceStatus.VERIFIED
    assert offer.organic_commission_amount.value == 181.9


def test_tiktok_sparse_invitation_does_not_invent_currency_or_price():
    offer = normalize_tiktok_invitation({
        "seller_name": "ANCUTRUTU shop",
        "title": "Flexible LED Display",
        "displayed_earnings_amount": 181.90,
        "shop_ads_commission_rate": 0.01,
        "free_sample_available": True,
    }, source="screenshot")
    assert offer.displayed_earnings_amount.value == 181.90
    assert offer.displayed_earnings_currency.status == EvidenceStatus.UNKNOWN
    assert offer.price_amount.status == EvidenceStatus.UNKNOWN
    assert offer.shop_ads_commission_rate.value == 0.01
    assert offer.free_sample_available.value is True


def test_tiktok_invitation_only_marks_currency_verified_when_explicit():
    offer = normalize_tiktok_invitation({
        "product_id":"p1", "title":"Producto", "price_amount": 500, "currency":"MXN",
        "organic_commission_rate":0.12, "shop_ads_commission_rate":"1%",
    }, source="product page")
    assert offer.currency.value == "MXN"
    assert offer.currency.status == EvidenceStatus.VERIFIED
    assert offer.shop_ads_commission_rate.value == 0.01
