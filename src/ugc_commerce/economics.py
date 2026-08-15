from __future__ import annotations

import math
from typing import Iterable

from pydantic import BaseModel, Field

from .offers import EvidenceStatus, EvidenceValue, ProductOfferSnapshot


class EconomicsScenario(BaseModel):
    name: str
    views: float = Field(default=1000, ge=0)
    ctr: float = Field(ge=0, le=1)
    cvr: float = Field(ge=0, le=1)


class ProductionCosts(BaseModel):
    sample_cost_mxn: float = Field(default=0, ge=0)
    generation_cost_mxn: float = Field(default=0, ge=0)
    editing_cost_mxn: float = Field(default=0, ge=0)
    other_cost_mxn: float = Field(default=0, ge=0)

    @property
    def total(self) -> float:
        return self.sample_cost_mxn + self.generation_cost_mxn + self.editing_cost_mxn + self.other_cost_mxn


class ScenarioProjection(BaseModel):
    name: str
    views: float
    ctr: float
    cvr: float
    clicks: float
    orders: float
    organic_revenue: float | None = None
    shop_ads_revenue: float | None = None
    organic_commission_per_1000_views: float | None = None
    shop_ads_commission_per_1000_views: float | None = None


class AffiliateEconomics(BaseModel):
    currency: str | None = None
    organic_commission_per_sale: float | None = None
    shop_ads_commission_per_sale: float | None = None
    total_test_cost_mxn: float = 0
    orders_to_break_even: int | None = None
    scenarios: list[ScenarioProjection] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)


def _verified_number(value: EvidenceValue) -> float | None:
    if value.status != EvidenceStatus.VERIFIED or value.value is None:
        return None
    try:
        return float(value.value)
    except (TypeError, ValueError):
        return None


def _verified_text(value: EvidenceValue) -> str | None:
    if value.status != EvidenceStatus.VERIFIED or value.value is None:
        return None
    text = str(value.value).strip()
    return text or None


def _commission_per_sale(*, amount: EvidenceValue, rate: EvidenceValue, price: EvidenceValue) -> float | None:
    verified_amount = _verified_number(amount)
    if verified_amount is not None:
        return verified_amount
    verified_rate = _verified_number(rate)
    verified_price = _verified_number(price)
    if verified_rate is None or verified_price is None:
        return None
    if not 0 <= verified_rate <= 1:
        return None
    return verified_price * verified_rate


def calculate_affiliate_economics(
    offer: ProductOfferSnapshot,
    *,
    scenarios: Iterable[EconomicsScenario] | None = None,
    costs: ProductionCosts | None = None,
) -> AffiliateEconomics:
    costs = costs or ProductionCosts()
    currency = _verified_text(offer.currency)
    organic = _commission_per_sale(
        amount=offer.organic_commission_amount,
        rate=offer.organic_commission_rate,
        price=offer.price_amount,
    )
    shop_ads = _commission_per_sale(
        amount=offer.shop_ads_commission_amount,
        rate=offer.shop_ads_commission_rate,
        price=offer.price_amount,
    )

    missing: list[str] = []
    if currency is None:
        missing.append("currency")
    if _verified_number(offer.price_amount) is None:
        missing.append("price")
    if organic is None:
        missing.append("organic_commission")
    if offer.shop_ads_commission_rate.is_known or offer.shop_ads_commission_amount.is_known:
        if shop_ads is None:
            missing.append("shop_ads_commission")

    total_cost = costs.total
    break_even = math.ceil(total_cost / organic) if organic is not None and organic > 0 and total_cost > 0 else None

    projections: list[ScenarioProjection] = []
    assumptions: list[str] = []
    for scenario in scenarios or []:
        clicks = scenario.views * scenario.ctr
        orders = clicks * scenario.cvr
        organic_revenue = orders * organic if organic is not None else None
        shop_ads_revenue = orders * shop_ads if shop_ads is not None else None
        per_1000_factor = 0 if scenario.views == 0 else 1000 / scenario.views
        projections.append(ScenarioProjection(
            name=scenario.name,
            views=scenario.views,
            ctr=scenario.ctr,
            cvr=scenario.cvr,
            clicks=clicks,
            orders=orders,
            organic_revenue=organic_revenue,
            shop_ads_revenue=shop_ads_revenue,
            organic_commission_per_1000_views=(organic_revenue * per_1000_factor if organic_revenue is not None else None),
            shop_ads_commission_per_1000_views=(shop_ads_revenue * per_1000_factor if shop_ads_revenue is not None else None),
        ))
        assumptions.append(f"{scenario.name}: views={scenario.views}, ctr={scenario.ctr}, cvr={scenario.cvr}")

    return AffiliateEconomics(
        currency=currency,
        organic_commission_per_sale=organic,
        shop_ads_commission_per_sale=shop_ads,
        total_test_cost_mxn=total_cost,
        orders_to_break_even=break_even,
        scenarios=projections,
        assumptions=assumptions,
        missing_data=list(dict.fromkeys(missing)),
    )
