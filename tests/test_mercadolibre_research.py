from ugc_commerce.mercadolibre_research import convert_catalog_offer, summarize_candidate_batch
from ugc_commerce.offers import EvidenceStatus


def ev(value, status="VERIFIED"):
    return {
        "value": value,
        "status": status,
        "source": "https://api.mercadolibre.com/products/MLM73110037/items",
        "observed_at": "2026-11-04T20:19:43.026Z",
    }


def catalog_with_offer():
    return {
        "id": "MLM73110037",
        "kind": "catalog",
        "source": "https://api.mercadolibre.com/products/MLM73110037",
        "fields": {
            "title": ev("Organizador De Despensa"),
            "category_id": ev(None, "UNKNOWN"),
        },
        "offers_status": "available",
        "offers": [
            {
                "id": "MLM5768786652",
                "kind": "item",
                "source": "https://api.mercadolibre.com/products/MLM73110037/items",
                "fields": {
                    "price": ev(2272),
                    "currency": ev("MXN"),
                    "seller_id": ev("1834732469"),
                    "affiliate_commission": ev(None, "UNKNOWN"),
                    "stock": ev(None, "UNKNOWN"),
                },
            }
        ],
    }


def test_verified_catalog_offer_becomes_snapshot_but_not_approved():
    catalog = catalog_with_offer()
    product = convert_catalog_offer(catalog, catalog["offers"][0])
    assert product is not None
    assert product.product_id == "MLM5768786652"
    assert product.price_amount.value == 2272
    assert product.price_amount.status == EvidenceStatus.VERIFIED
    assert product.currency.value == "MXN"
    assert product.organic_commission_amount.status == EvidenceStatus.UNKNOWN
    assert product.stock_status.status == EvidenceStatus.UNKNOWN
    assert product.commercial_rights_status == "pending"
    assert product.affiliate_url is None
    assert product.media_assets == []
    assert product.source_provenance


def test_seller_name_requires_matching_verified_seller_id():
    catalog = catalog_with_offer()
    seller = {"id": "1834732469", "fields": {"nickname": ev("WW20240530191221")}}
    offer = catalog["offers"][0]
    assert convert_catalog_offer(catalog, offer, seller=seller).seller_name == "WW20240530191221"
    assert convert_catalog_offer(
        catalog, offer, seller={"id": "999", "fields": {"nickname": ev("Otro")}}
    ).seller_name is None


def test_unknown_or_inferred_price_not_marked_verified():
    catalog = catalog_with_offer()
    offer = catalog["offers"][0]
    offer["fields"]["price"] = ev(999, "UNKNOWN")
    product = convert_catalog_offer(catalog, offer)
    assert product is not None
    assert product.price_amount.value is None
    assert product.price_amount.status == EvidenceStatus.UNKNOWN


def test_catalogue_title_and_listing_id_are_required():
    catalog = catalog_with_offer()
    offer = catalog["offers"][0]
    catalog["fields"]["title"] = ev(None, "UNKNOWN")
    assert convert_catalog_offer(catalog, offer) is None
    catalog["fields"]["title"] = ev("Organizador")
    offer["id"] = "INVALID"
    assert convert_catalog_offer(catalog, offer) is None


def test_batch_summary_does_not_confuse_catalogue_count_with_verified_offers():
    good = catalog_with_offer()
    not_found = {
        "id": "MLM78426751",
        "kind": "catalog",
        "offers_status": "unavailable",
        "offers_error": {"code": "not_found", "http_status": 404},
        "offers": [],
    }
    not_requested = {
        "id": "MLM74953700", "kind": "catalog",
        "offers_status": "not_requested",
    }
    report = summarize_candidate_batch({
        "site_id": "MLM",
        "status": "ok",
        "candidates": [good, not_found, not_requested],
        "failures": [],
    })
    assert report["catalogs_returned"] == 3
    assert report["catalogues_queried_for_offers"] == 2
    assert report["catalogues_without_offer_lookup"] == 1
    assert report["catalogues_with_offers"] == 1
    assert report["offer_lookup_failures"] == {"not_found": 1}
    assert report["offers_returned"] == 1
    assert report["offers_with_verified_price_and_currency"] == 1
    assert report["offers_with_verified_seller_id"] == 1
    assert report["affiliate_commission_verified"] == 0
    assert report["production_approval"] == "NEEDS_DATA"


def test_empty_catalogue_offer_lookup_counts_as_attempt_not_as_available_offer():
    empty = {
        "id": "MLM999000111",
        "kind": "catalog",
        "offers_status": "empty",
        "offers": [],
    }
    report = summarize_candidate_batch({"site_id": "MLM", "candidates": [empty]})
    assert report["catalogs_returned"] == 1
    assert report["catalogues_queried_for_offers"] == 1
    assert report["catalogues_with_offers"] == 0
    assert report["catalogues_with_empty_offer_response"] == 1
    assert report["catalogues_without_offer_lookup"] == 0
    assert report["offer_lookup_failures"] == {}
    assert report["offers_returned"] == 0
    assert report["affiliate_commission_verified"] == 0
    assert report["production_approval"] == "NEEDS_DATA"


def test_mixed_offer_states_count_attempts_separately_from_missing_lookup():
    available = catalog_with_offer()
    empty = {"id": "MLM111222333", "kind": "catalog", "offers_status": "empty", "offers": []}
    blocked = {
        "id": "MLM444555666", "kind": "catalog", "offers_status": "unavailable",
        "offers_error": {"code": "not_found", "http_status": 404}, "offers": [],
    }
    untouched = {"id": "MLM777888999", "kind": "catalog", "offers_status": "not_requested"}
    report = summarize_candidate_batch({
        "site_id": "MLM", "candidates": [available, empty, blocked, untouched]
    })
    assert report["catalogues_queried_for_offers"] == 3
    assert report["catalogues_with_offers"] == 1
    assert report["catalogues_with_empty_offer_response"] == 1
    assert report["catalogues_without_offer_lookup"] == 1
    assert report["offer_lookup_failures"] == {"not_found": 1}
    assert report["offers_returned"] == 1
    assert report["production_approval"] == "NEEDS_DATA"
