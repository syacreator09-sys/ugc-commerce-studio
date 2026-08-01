from __future__ import annotations

from .domain import ProductManifest


class ProductValidationError(ValueError):
    pass


def validate_product(product: ProductManifest) -> list[str]:
    warnings: list[str] = []

    if product.commercial_rights_status != "approved":
        raise ProductValidationError("commercial rights are not approved")
    if product.availability not in {"available", "in_stock"}:
        raise ProductValidationError("product is not currently available")
    if not product.verified_benefits:
        raise ProductValidationError("verified benefits are required")
    if not product.source_url and not product.media_assets:
        raise ProductValidationError("source URL or authorized product media is required")

    platform = product.platform.lower()
    if product.ownership_type == "affiliate":
        if not product.affiliate_url:
            raise ProductValidationError("affiliate products require an affiliate URL")
        if product.commission_value is None:
            warnings.append("commission_not_verified")

    if platform in {"amazon", "amazon_mx", "amazon_associates"}:
        if not product.source_url:
            raise ProductValidationError("Amazon products require a source product URL")
        warnings.append("amazon_price_and_availability_must_be_refreshed_before_publish")

    elif platform in {"mercadolibre", "mercado_libre", "meli"}:
        warnings.append("mercadolibre_commission_must_be_date_stamped")

    elif platform in {"tiktok_shop", "tiktok"}:
        warnings.append("manual_product_anchor_required")

    elif platform in {"own_store", "shopify", "woocommerce"}:
        if product.ownership_type == "owned" and product.affiliate_url:
            warnings.append("owned_product_contains_affiliate_url")

    return warnings
