"""Inspect per-sale Mercado Libre affiliate commission offers supplied as evidence.

No commission API is assumed. Inputs must come from a verified affiliate dashboard,
campaign record, or authorized capture, not general listing data.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Literal

from pydantic import BaseModel, Field

from .offers import EvidenceStatus, EvidenceValue


class AffiliateCommissionOffer(BaseModel):
    """All rates are percentages (e.g. 15 means 15%), never decimal fractions."""
    item_id: str
    placement: Literal["ml_affiliates", "youtube_shopping", "facebook_affiliates"] = "ml_affiliates"
    price_mxn: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    currency: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    eligible: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    category_rate_pct: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    seller_extra_rate_pct: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    displayed_total_rate_pct: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    displayed_payout_mxn: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    stacking_confirmed: EvidenceValue = Field(default_factory=EvidenceValue.unknown)
    captured_at: datetime | None = None
    valid_until: datetime | None = None
    evidence_ref: str | None = None


def _decimal(evidence: EvidenceValue, *, upper: Decimal | None = None) -> Decimal | None:
    if not evidence.is_verified or isinstance(evidence.value, bool):
        return None
    try:
        amount = Decimal(str(evidence.value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not amount.is_finite() or amount < 0 or (upper is not None and amount > upper):
        return None
    return amount


def _money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def evaluate_commission(
    offer: AffiliateCommissionOffer,
    *,
    now: datetime | None = None,
    expected_item_id: str | None = None,
    expected_price_mxn: Decimal | None = None,
    max_age_hours: int = 24,
) -> dict:
    """Never promise a payment or add rates without verified stacking rules."""
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    if not re.fullmatch(r"MLM\d{1,20}", offer.item_id):
        raise ValueError("invalid Mercado Libre Mexico item ID")
    if expected_item_id is not None and expected_item_id != offer.item_id:
        raise ValueError("commission belongs to a different listing")
    if max_age_hours <= 0:
        raise ValueError("max_age_hours must be positive")
    base = _decimal(offer.category_rate_pct, upper=Decimal(100))
    extra = _decimal(offer.seller_extra_rate_pct, upper=Decimal(100))
    total = _decimal(offer.displayed_total_rate_pct, upper=Decimal(100))
    price = _decimal(offer.price_mxn)
    payout = _decimal(offer.displayed_payout_mxn)
    result = {
        "item_id": offer.item_id,
        "placement": offer.placement,
        "category_rate_pct": str(base) if base is not None else None,
        "seller_extra_rate_pct": str(extra) if extra is not None else None,
        "total_rate_pct": None,
        "offered_per_sale_mxn": None,
        "amount_status": "UNKNOWN",
        "basis": None,
        "eligible": offer.eligible.value if offer.eligible.is_verified else None,
        "campaign_valid_until": offer.valid_until.isoformat() if offer.valid_until else None,
        "captured_at": offer.captured_at.isoformat() if offer.captured_at else None,
        "evidence_ref": offer.evidence_ref,
        "production_decision": "NEEDS_DATA",
    }
    if not offer.currency.is_verified or offer.currency.value != "MXN":
        result["basis"] = "CURRENCY_UNVERIFIED_OR_NON_MXN"
        return result
    if offer.eligible.is_verified and offer.eligible.value is False:
        result["basis"] = "NOT_ELIGIBLE"
        return result
    if not offer.evidence_ref or not offer.captured_at:
        result["basis"] = "MISSING_AFFILIATE_PANEL_EVIDENCE"
        return result
    if offer.captured_at.tzinfo is None:
        raise ValueError("captured_at must be timezone-aware")
    if offer.captured_at > now + timedelta(minutes=5):
        result["basis"] = "FUTURE_CAPTURE"
        return result
    if now - offer.captured_at > timedelta(hours=max_age_hours):
        result["basis"] = "STALE_COMMISSION_CAPTURE"
        return result
    if offer.valid_until is not None:
        if offer.valid_until.tzinfo is None:
            raise ValueError("valid_until must be timezone-aware")
        if offer.valid_until < now:
            result["basis"] = "EXPIRED_CAMPAIGN"
            return result
    if expected_price_mxn is not None and (
        price is None or abs(price - expected_price_mxn) > Decimal("0.01")
    ):
        result["basis"] = "PRICE_MISMATCH"
        return result

    if total is not None:
        result["total_rate_pct"] = str(total)
    elif base is not None and extra is not None:
        if offer.stacking_confirmed.is_verified and offer.stacking_confirmed.value is True:
            total = base + extra
            if total > 100:
                result["basis"] = "RATE_CONFLICT"
                return result
            result["total_rate_pct"] = str(total)
        else:
            result["basis"] = "STACKING_NOT_CONFIRMED"

    if payout is not None:
        if total is not None and price is not None:
            computed = (price * total / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if abs(computed - payout) > Decimal("0.02"):
                result["basis"] = "RATE_PAYOUT_CONFLICT"
                result["total_rate_pct"] = None
                return result
        result["offered_per_sale_mxn"] = _money(payout)
        result["amount_status"] = EvidenceStatus.VERIFIED.value
        result["basis"] = "AFFILIATE_PANEL_DISPLAYED_AMOUNT"
    elif total is not None and price is not None:
        result["offered_per_sale_mxn"] = _money(price * total / 100)
        result["amount_status"] = EvidenceStatus.ESTIMATED.value
        result["basis"] = "CALCULATED_FROM_VERIFIED_RATE_AND_PRICE"
    elif result["basis"] is None:
        result["basis"] = "NO_VERIFIED_TOTAL_COMMISSION"

    if (
        result["offered_per_sale_mxn"] is not None
        and offer.eligible.is_verified
        and offer.eligible.value is True
    ):
        result["production_decision"] = "COMMISSION_REVIEWED"
    return result


def summarize_commissions(offers: list[AffiliateCommissionOffer], *, now: datetime | None = None) -> dict:
    rows = [evaluate_commission(x, now=now) for x in offers]
    return {
        "offers_checked": len(rows),
        "offered_payout_visible": sum(r["offered_per_sale_mxn"] is not None for r in rows),
        "offers_with_displayed_verified_amount": sum(r["amount_status"] == "VERIFIED" for r in rows),
        "offers_with_calculated_estimate": sum(r["amount_status"] == "ESTIMATED" for r in rows),
        "offers_without_payout": sum(r["offered_per_sale_mxn"] is None for r in rows),
        "rows": rows,
        "warning": "Amounts are conditional offers, not earned or paid commissions. Separate commercial/UGC gates still apply.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline affiliate commission evidence report")
    parser.add_argument("json_file", help="JSON with {'offers': [AffiliateCommissionOffer...]}")
    args = parser.parse_args()
    with open(args.json_file, encoding="utf-8") as f:
        data = json.load(f)
    print(json.dumps(
        summarize_commissions([AffiliateCommissionOffer.model_validate(item) for item in data["offers"]]),
        ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
