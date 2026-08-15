from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from pydantic import BaseModel, Field

from .confidence import ConfidenceReport, assess_data_confidence
from .creative_capacity import CreativeCapacityInput, CreativeCapacityReport, assess_creative_capacity
from .decisions import DecisionReport, ProductionDecision, SampleDecision, decide_product
from .economics import AffiliateEconomics, EconomicsScenario, ProductionCosts, calculate_affiliate_economics
from .offers import ProductOfferSnapshot
from .product_scout_score import ProductScoutInput, ProductScoutScore, score_product


class ProductIntelligenceReport(BaseModel):
    product_id: str
    title: str
    platform: str
    seller_name: str | None = None
    source_provenance: list[str] = Field(default_factory=list)
    data_quality: ConfidenceReport
    economics: AffiliateEconomics
    ugc_fit_raw_score: int
    ugc_fit_normalized_score: float
    ugc_legacy_decision: str
    ugc_score: ProductScoutScore
    creative_capacity: CreativeCapacityReport
    demand: dict[str, object | None]
    risk: list[str] = Field(default_factory=list)
    sample_decision: SampleDecision
    production_decision: ProductionDecision
    recommended_initial_creatives: int | str = 0
    why: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)
    next_action: str


def analyze_product_offer(
    offer: ProductOfferSnapshot,
    scout_input: ProductScoutInput,
    creative_input: CreativeCapacityInput,
    *,
    scenarios: Iterable[EconomicsScenario] | None = None,
    costs: ProductionCosts | None = None,
) -> ProductIntelligenceReport:
    economics = calculate_affiliate_economics(offer, scenarios=scenarios, costs=costs)
    commission_mxn = (
        economics.organic_commission_per_sale
        if economics.currency is not None and economics.currency.upper() == "MXN"
        else None
    )
    effective_scout_input = replace(scout_input, commission_mxn=commission_mxn)
    ugc = score_product(effective_scout_input)
    confidence = assess_data_confidence(offer)
    creative = assess_creative_capacity(creative_input)
    decision: DecisionReport = decide_product(
        offer=offer,
        economics=economics,
        confidence=confidence,
        ugc_score=ugc,
        creative_capacity=creative,
    )

    missing = list(dict.fromkeys([*confidence.missing_data, *economics.missing_data]))
    risk = [*decision.hard_gates]
    if offer.prohibited_claims:
        risk.append("prohibited claims present: " + ", ".join(offer.prohibited_claims))
    if effective_scout_input.requires_physical_demo_without_vto:
        risk.append("physical product demonstration required")
    if offer.has_known_platform_restrictions:
        risk.append("known platform restriction")
    if offer.has_blocking_platform_restrictions and "blocking platform restriction makes offer non-viable" not in risk:
        risk.append("blocking platform restriction")

    demand = {
        "sales": offer.sales_count.value,
        "orders": offer.orders_count.value,
        "reviews": offer.review_count.value,
        "rating": offer.rating.value,
        "stock": offer.stock_status.value,
        "trend": offer.trend_signal.value,
    }

    if decision.production_decision == ProductionDecision.RECHAZADO:
        next_action = "Do not produce; resolve hard gate or reject product."
    elif decision.sample_decision == SampleDecision.SOLICITAR and decision.production_decision == ProductionDecision.PROCEDE:
        next_action = "Request sample if useful, then create the recommended small UGC test batch after exact approval."
    elif missing:
        next_action = "Verify missing commercial data before spending premium generation credits: " + ", ".join(missing)
    else:
        next_action = "Hold for operator review before premium generation."

    return ProductIntelligenceReport(
        product_id=offer.product_id,
        title=offer.title,
        platform=offer.platform,
        seller_name=offer.seller_name,
        source_provenance=list(dict.fromkeys(offer.source_provenance)),
        data_quality=confidence,
        economics=economics,
        ugc_fit_raw_score=ugc.raw_score,
        ugc_fit_normalized_score=ugc.normalized_score,
        ugc_legacy_decision=ugc.decision.value,
        ugc_score=ugc,
        creative_capacity=creative,
        demand=demand,
        risk=risk,
        sample_decision=decision.sample_decision,
        production_decision=decision.production_decision,
        recommended_initial_creatives=decision.recommended_initial_creatives,
        why=decision.reasons,
        missing_data=missing,
        next_action=next_action,
    )
