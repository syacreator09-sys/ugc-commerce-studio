from __future__ import annotations

from .domain import ProductManifest


def opportunity_score(product: ProductManifest) -> dict:
    score = 0.0
    reasons: list[str] = []

    if product.availability == "available":
        score += 20
        reasons.append("available")
    if product.price_amount is not None:
        score += 10
        reasons.append("price_verified")
    if product.verified_benefits:
        score += min(25, len(product.verified_benefits) * 10)
        reasons.append("verified_benefits")
    if len(product.media_assets) >= 3:
        score += 20
        reasons.append("strong_product_references")
    if product.commercial_rights_status == "approved":
        score += 15
        reasons.append("commercial_rights_approved")
    if product.ownership_type == "affiliate" and product.affiliate_url:
        score += 10
        reasons.append("affiliate_attribution_ready")

    score = min(score, 100.0)
    recommendation = (
        "PREMIUM_PRODUCTION" if score >= 75 else
        "TEST_UGC" if score >= 55 else
        "WATCH" if score >= 35 else
        "REJECT"
    )
    return {"score": score, "recommendation": recommendation, "reasons": reasons}


def creative_matrix(product: ProductManifest) -> dict:
    benefit = product.verified_benefits[0] if product.verified_benefits else "beneficio pendiente de validar"
    return {
        "product_id": product.product_id,
        "audiences": ["problem-aware buyers", "comparison shoppers", "impulse buyers"],
        "angles": ["honest review", "problem-solution", "quick demonstration", "objection answer"],
        "hooks": [
            f"Pensé que {product.title} era otro producto más.",
            f"Esto es lo primero que revisaría antes de comprar {product.title}.",
            f"Lo probé porque {benefit}.",
        ],
        "formats": ["ugc", "product_review", "ugc_how_to"],
        "blocked_claims": product.prohibited_claims,
    }
