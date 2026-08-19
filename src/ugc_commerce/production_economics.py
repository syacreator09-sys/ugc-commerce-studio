from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from .economics import EconomicsScenario, ProductionCosts, calculate_affiliate_economics
from .offers import ProductOfferSnapshot
from .priors import CommercePerformancePriorV1, prior_matches_platform


class CostBenefitRecommendation(StrEnum):
    NEEDS_DATA = "NEEDS_DATA"
    NOT_ECONOMIC = "NOT_ECONOMIC"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"


class ProductionEconomicsInput(BaseModel):
    costs: ProductionCosts = Field(default_factory=ProductionCosts)
    scenarios: list[EconomicsScenario] = Field(default_factory=list)
    historical_prior: CommercePerformancePriorV1 | None = None
    prior_context: dict[str, str] = Field(default_factory=dict)
    prior_min_sample_size: int = Field(default=5, ge=2)
    prior_min_confidence: int = Field(default=55, ge=0, le=100)
    base_views: float = Field(default=5000, gt=0)


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
    historical_prior_id: str | None = None
    historical_prior_applied: bool = False
    historical_prior_source_refs: list[str] = Field(default_factory=list)
    recommendation: CostBenefitRecommendation
    reasons: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


def _effective_prior_context(offer: ProductOfferSnapshot, supplied: dict[str, str]) -> dict[str, str]:
    context = {
        "product_id": offer.product_id,
        "market": offer.market,
        "content_type": "ugc-commerce",
    }
    if offer.category:
        context["category"] = offer.category
    if offer.seller_name:
        context["seller_name"] = offer.seller_name
    context.update({str(key).strip(): str(value).strip() for key, value in supplied.items() if str(key).strip() and str(value).strip()})
    return context


def _prior_filters_match(prior: CommercePerformancePriorV1, context: dict[str, str]) -> tuple[bool, list[str]]:
    mismatches: list[str] = []
    for key, expected in prior.filters.items():
        actual = context.get(key)
        if actual is None:
            mismatches.append(f"{key}=<missing> expected {expected}")
        elif str(actual) != str(expected):
            mismatches.append(f"{key}={actual} expected {expected}")
    return not mismatches, mismatches


def _resolve_scenarios(
    offer: ProductOfferSnapshot,
    economics_input: ProductionEconomicsInput,
) -> tuple[list[EconomicsScenario], bool, list[str]]:
    prior = economics_input.historical_prior
    if economics_input.scenarios:
        notes = []
        if prior is not None:
            notes.append(f"explicit scenario CTR/CVR override historical prior {prior.prior_id}")
        return economics_input.scenarios, False, notes
    if prior is None:
        return [], False, []
    if not prior_matches_platform(prior, offer.platform):
        return [], False, [f"historical prior {prior.prior_id} ignored: platform mismatch"]
    if not prior.usable(
        min_sample_size=economics_input.prior_min_sample_size,
        min_confidence=economics_input.prior_min_confidence,
    ):
        return [], False, [f"historical prior {prior.prior_id} ignored: insufficient comparable evidence"]

    context = _effective_prior_context(offer, economics_input.prior_context)
    matches, mismatches = _prior_filters_match(prior, context)
    if not matches:
        return [], False, [
            f"historical prior {prior.prior_id} ignored: filter context mismatch ({'; '.join(mismatches)})"
        ]

    assert prior.ctr_median is not None and prior.cvr_median is not None
    ctr = prior.ctr_median
    cvr = prior.cvr_median
    scenarios = [
        EconomicsScenario(
            name="conservative",
            views=max(1000.0, economics_input.base_views * 0.2),
            ctr=max(0.0, ctr * 0.75),
            cvr=max(0.0, cvr * 0.75),
        ),
        EconomicsScenario(name="base", views=economics_input.base_views, ctr=ctr, cvr=cvr),
        EconomicsScenario(
            name="aggressive",
            views=economics_input.base_views * 2,
            ctr=min(1.0, ctr * 1.25),
            cvr=min(1.0, cvr * 1.25),
        ),
    ]
    filter_note = ", ".join(f"{key}={value}" for key, value in sorted(prior.filters.items())) or "unsegmented"
    return scenarios, True, [
        f"base CTR/CVR use MIO prior {prior.prior_id} from {prior.sample_size} comparable records at {prior.window_hours}h ({filter_note})",
        "conservative/aggressive prior scenarios scale median CTR/CVR by 0.75x/1.25x; they remain estimates",
    ]


def analyze_production_cost_benefit(
    offer: ProductOfferSnapshot,
    economics_input: ProductionEconomicsInput,
) -> ProductionBenefitReport:
    scenarios, prior_applied, prior_notes = _resolve_scenarios(offer, economics_input)
    economics = calculate_affiliate_economics(
        offer,
        scenarios=scenarios,
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

    prior = economics_input.historical_prior
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
        historical_prior_id=prior.prior_id if prior is not None else None,
        historical_prior_applied=prior_applied,
        historical_prior_source_refs=list(prior.source_refs) if prior is not None else [],
        recommendation=recommendation,
        reasons=reasons,
        missing_data=list(dict.fromkeys(missing)),
        assumptions=[*economics.assumptions, *prior_notes],
    )
