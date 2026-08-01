import pytest

from ugc_commerce.domain import ProductManifest
from ugc_commerce.sources import ProductValidationError, validate_product


def base_product(**updates):
    product = ProductManifest(
        product_id="p1",
        ownership_type="affiliate",
        platform="tiktok_shop",
        title="Producto",
        source_url="https://example.com/product",
        affiliate_url="https://example.com/affiliate",
        availability="available",
        verified_benefits=["beneficio verificado"],
        media_assets=["front.jpg", "side.jpg", "detail.jpg"],
        commercial_rights_status="approved",
    )
    return product.model_copy(update=updates)


def test_tiktok_requires_manual_anchor_warning():
    warnings = validate_product(base_product())
    assert "manual_product_anchor_required" in warnings


def test_affiliate_link_is_required():
    with pytest.raises(ProductValidationError):
        validate_product(base_product(affiliate_url=None))


def test_unavailable_product_is_blocked():
    with pytest.raises(ProductValidationError):
        validate_product(base_product(availability="out_of_stock"))
