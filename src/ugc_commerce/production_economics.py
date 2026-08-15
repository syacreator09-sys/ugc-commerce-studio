from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from .economics import EconomicsScenario, ProductionCosts, calculate_affiliate_economics
from .offers import ProductOfferSnapshot


class CostBenefitRecommendation(StrEnum):
    NEEDS_DATA = "NEEDS_DATA"
    NOT_ECONOMIC = "NOT_ECONOMIC"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"


class ProductionEconomicsInput(BaseModel):
    costs: ProductionCosts = Field(default_factory=ProductionCosts)
    scenarios: list[EconomicsScenario] = Field(min_length=1)


class ProductionBenefitProjection(BaseModel):
    name: str
    views: float
    ctr: float
    cvr: float
    expected_orders: float
    expected_organic_commission: float | None = None
    expected_shop_ads_commission: float | None = None
    total_test_cost: float
    net_benefit: float | None = None
    roi: float | None = None
    break_even_views: float | None = None


class ProductionBenefitReport(BaseModel):
    currency: str | None = None
    total_test_cost: float
    organic_commission_per_sale: float | None = None
    shop_ads_commission_per_sale: float | None = None
    orders_to_break_even: int | None = None
    projections: list[ProductionBenefitProjection] = Field(default_factory=list)
    base_scenario: str | None = None
    base_expected_commission: float | None = None
    base_net_benefit: float | None = None
    base_roi: float | None = None
    recommendation: CostBenefitRecommendation
    reasons: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


def analyze_production_cost_benefit(
    offer: ProductOfferSnapshot,
    economics_input: ProductionEconomicsInput,
) -> ProductionBenefitReport:
    economics = calculate_affiliate_economics(
        offer,
        scenarios=economics_input.scenarios,
        costs=economics_input.costs,
    )
    missing = list(economics.missing_data)
    reasons: list[str] = []

    currency_matches = (
        economics.currency is not None
        and economics.currency.upper() == economics.test_cost_currency.upper()
    )
    if not currency_matches:
        if "cost_currency_mismatch" not in missing:
            missing.append("cost_currency_mismatch")

    projections: list[ProductionBenefitProjection] = []
    commission = economics.organic_commission_per_sale
    total_cost = economics.total_test_cost_mxn
    for projection in economics.scenarios:
        expected = projection.expected_organic_commission_per_video
        net = expected - total_cost if expected is not None and currency_matches else None
        roi = None
        if net is not None and total_cost > 0:
            roi = net / total_cost
        revenue_per_view = (
            projection.ctr * projection.cvr * commission
            if commission is not None and commission > 0
            else 0
        )
        break_even_views = (
            total_cost / revenue_per_view
            if total_cost > 0 and revenue_per_view > 0 and currency_matches
            else (0.0 if total_cost == 0 and revenue_per_view > 0 and currency_matches else None)
        )
        projections.append(ProductionBenefitProjection(
            name=projection.name,
            views=projection.views,
            ctr=projection.ctr,
            cvr=projection.cvr,
            expected_orders=projection.orders,
            expected_organic_commission=expected,
            expected_shop_ads_commission=projection.expected_shop_ads_commission_per_video,
            total_test_cost=total_cost,
            net_benefit=net,
            roi=roi,
            break_even_views=break_even_views,
        ))

    base = next((item for item in projections if item.name.lower() == "base"), None)
    if base is None:
        missing.append("base_scenario")

    if economics.currency is None or commission is None or not currency_matches or base is None:
        recommendation = CostBenefitRecommendation.NEEDS_DATA
        reasons.append("cost/benefit cannot be compared with sufficient verified economics")
    elif commission <= 0:
        recommendation = CostBenefitRecommendation.NOT_ECONOMIC
        reasons.append("organic commission per sale is zero or non-positive")
    elif base.net_benefit is None:
        recommendation = CostBenefitRecommendation.NEEDS_DATA
        reasons.append("base net benefit could not be calculated")
    elif base.net_benefit < 0:
        recommendation = CostBenefitRecommendation.NOT_ECONOMIC
        reasons.append("base scenario does not recover the explicit test cost")
    else:
        recommendation = CostBenefitRecommendation.APPROVAL_REQUIRED
        reasons.append("base scenario covers explicit test cost; human approval is still required")

    return ProductionBenefitReport(
        currency=economics.currency,
        total_test_cost=total_cost,
        organic_commission_per_sale=commission,
        shop_ads_commission_per_sale=economics.shop_ads_commission_per_sale,
        orders_to_break_even=economics.orders_to_break_even,
        projections=projections,
        base_scenario=base.name if base else None,
        base_expected_commission=base.expected_organic_commission if base else None,
        base_net_benefit=base.net_benefit if base else None,
        base_roi=base.roi if base else None,
        recommendation=recommendation,
        reasons=reasons,
        missing_data=list(dict.fromkeys(missing)),
        assumptions=economics.assumptions,
    )
