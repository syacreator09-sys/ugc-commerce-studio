from __future__ import annotations

from pydantic import BaseModel, Field


class PublicationPerformance(BaseModel):
    product_id: str
    creative_id: str
    hook_id: str | None = None
    video_id: str | None = None
    channel: str | None = None
    category: str | None = None
    format: str | None = None
    views: int = Field(default=0, ge=0)
    product_clicks: int = Field(default=0, ge=0)
    orders: int = Field(default=0, ge=0)
    gmv_mxn: float = Field(default=0, ge=0)
    organic_commission_mxn: float = Field(default=0, ge=0)
    shop_ads_commission_mxn: float = Field(default=0, ge=0)
    retention_pct: float | None = Field(default=None, ge=0)


class PerformanceMetrics(BaseModel):
    product_id: str
    creative_id: str
    views: int
    product_clicks: int
    orders: int
    ctr: float
    cvr: float
    gmv_mxn: float
    organic_commission_mxn: float
    shop_ads_commission_mxn: float
    total_commission_mxn: float
    commission_per_view: float
    commission_per_1000_views: float
    commission_per_order: float


def calculate_performance(data: PublicationPerformance) -> PerformanceMetrics:
    total = data.organic_commission_mxn + data.shop_ads_commission_mxn
    ctr = data.product_clicks / data.views if data.views else 0.0
    cvr = data.orders / data.product_clicks if data.product_clicks else 0.0
    commission_per_view = total / data.views if data.views else 0.0
    commission_per_1000_views = commission_per_view * 1000
    commission_per_order = total / data.orders if data.orders else 0.0
    return PerformanceMetrics(
        product_id=data.product_id,
        creative_id=data.creative_id,
        views=data.views,
        product_clicks=data.product_clicks,
        orders=data.orders,
        ctr=ctr,
        cvr=cvr,
        gmv_mxn=data.gmv_mxn,
        organic_commission_mxn=data.organic_commission_mxn,
        shop_ads_commission_mxn=data.shop_ads_commission_mxn,
        total_commission_mxn=total,
        commission_per_view=commission_per_view,
        commission_per_1000_views=commission_per_1000_views,
        commission_per_order=commission_per_order,
    )
