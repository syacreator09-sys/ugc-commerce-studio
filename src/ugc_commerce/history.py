from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from .performance import PublicationPerformance


HistoryDimension = Literal[
    "channel",
    "category",
    "hook_id",
    "format",
    "seller_name",
    "price_band",
    "presenter_id",
    "ugc_angle",
]


class HistoricalBaseline(BaseModel):
    dimension: str
    key: str
    observations: int
    views: int
    product_clicks: int
    orders: int
    total_commission_mxn: float
    ctr: float
    cvr: float
    commission_per_1000_views: float


def append_history(path: Path, record: PublicationPerformance) -> None:
    """Append one real observation to an owned JSONL performance dataset."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(record.model_dump_json())
        handle.write("\n")


def load_history(path: Path) -> list[PublicationPerformance]:
    """Load persisted observations without fabricating a baseline for missing files."""
    if not path.exists():
        return []
    records: list[PublicationPerformance] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                records.append(PublicationPerformance.model_validate_json(text))
            except Exception as error:
                raise ValueError(f"invalid performance history at line {line_number}: {error}") from error
    return records


def build_baselines(records: list[PublicationPerformance], *, dimension: HistoryDimension) -> list[HistoricalBaseline]:
    groups: dict[str, list[PublicationPerformance]] = defaultdict(list)
    for record in records:
        key = getattr(record, dimension)
        if key:
            groups[str(key)].append(record)

    result: list[HistoricalBaseline] = []
    for key, items in sorted(groups.items()):
        views = sum(item.views for item in items)
        clicks = sum(item.product_clicks for item in items)
        orders = sum(item.orders for item in items)
        commission = sum(item.organic_commission_mxn + item.shop_ads_commission_mxn for item in items)
        ctr = clicks / views if views else 0.0
        cvr = orders / clicks if clicks else 0.0
        per_1000 = commission / views * 1000 if views else 0.0
        result.append(HistoricalBaseline(
            dimension=dimension,
            key=key,
            observations=len(items),
            views=views,
            product_clicks=clicks,
            orders=orders,
            total_commission_mxn=commission,
            ctr=ctr,
            cvr=cvr,
            commission_per_1000_views=per_1000,
        ))
    return result


def best_baseline(baselines: list[HistoricalBaseline]) -> HistoricalBaseline | None:
    if not baselines:
        return None
    return max(baselines, key=lambda b: (b.commission_per_1000_views, b.observations, b.views))
