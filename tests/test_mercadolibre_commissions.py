from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from ugc_commerce.mercadolibre_commissions import (
    AffiliateCommissionOffer,
    evaluate_commission,
    summarize_commissions,
)
from ugc_commerce.offers import EvidenceValue

NOW = datetime(2026, 11, 5, 16, 0, tzinfo=timezone.utc)
REF = "affiliate-dashboard:capture-20261105-001"


def verified(value):
    return EvidenceValue.verified(value, source=REF)


def offer(**overrides):
    args = {
        "item_id": "MLM5768786652",
        "price_mxn": verified(800),
        "currency": verified("MXN"),
        "eligible": verified(True),
        "captured_at": NOW,
        "evidence_ref": REF,
    }
    args.update(overrides)
    return AffiliateCommissionOffer(**args)


def test_offered_amount_displayed_by_authorized_panel_is_verifiable_not_realized():
    result = evaluate_commission(
        offer(displayed_payout_mxn=verified(120)), now=NOW
    )
    assert result["offered_per_sale_mxn"] == "120.00"
    assert result["amount_status"] == "VERIFIED"
    assert result["basis"] == "AFFILIATE_PANEL_DISPLAYED_AMOUNT"
    assert result["production_decision"] == "COMMISSION_REVIEWED"


def test_verified_total_percentage_produces_estimate_not_verified_payout():
    result = evaluate_commission(
        offer(displayed_total_rate_pct=verified(15)), now=NOW
    )
    assert result["offered_per_sale_mxn"] == "120.00"
    assert result["total_rate_pct"] == "15"
    assert result["amount_status"] == "ESTIMATED"


def test_base_and_extra_do_not_stack_automatically():
    result = evaluate_commission(
        offer(category_rate_pct=verified(8), seller_extra_rate_pct=verified(7)), now=NOW
    )
    assert result["offered_per_sale_mxn"] is None
    assert result["basis"] == "STACKING_NOT_CONFIRMED"
    assert result["total_rate_pct"] is None


def test_stacking_requires_explicit_verified_confirmation():
    result = evaluate_commission(
        offer(
            category_rate_pct=verified(8),
            seller_extra_rate_pct=verified(7),
            stacking_confirmed=verified(True),
        ),
        now=NOW,
    )
    assert result["offered_per_sale_mxn"] == "120.00"
    assert result["amount_status"] == "ESTIMATED"
    assert result["total_rate_pct"] == "15"


def test_eligible_unknown_is_not_approved_even_if_offer_visible():
    result = evaluate_commission(
        offer(eligible=EvidenceValue.unknown(), displayed_payout_mxn=verified(120)),
        now=NOW,
    )
    assert result["amount_status"] == "VERIFIED"
    assert result["production_decision"] == "NEEDS_DATA"


def test_expired_offer_is_not_used_for_estimate():
    result = evaluate_commission(
        offer(displayed_total_rate_pct=verified(20), valid_until=NOW - timedelta(seconds=1)),
        now=NOW,
    )
    assert result["basis"] == "EXPIRED_CAMPAIGN"
    assert result["offered_per_sale_mxn"] is None


def test_stale_or_missing_capture_returns_no_payout():
    stale = offer(displayed_total_rate_pct=verified(20), captured_at=NOW - timedelta(days=2))
    assert evaluate_commission(stale, now=NOW)["basis"] == "STALE_COMMISSION_CAPTURE"
    missing = offer(displayed_total_rate_pct=verified(20), evidence_ref=None)
    assert evaluate_commission(missing, now=NOW)["basis"] == "MISSING_AFFILIATE_PANEL_EVIDENCE"


def test_currency_is_mxn_and_conflicting_price_blocks_estimate():
    result = evaluate_commission(
        offer(displayed_total_rate_pct=verified(10)),
        now=NOW,
        expected_price_mxn=Decimal("999.00"),
    )
    assert result["basis"] == "PRICE_MISMATCH"
    assert result["offered_per_sale_mxn"] is None


def test_verified_panel_amount_conflicting_with_displayed_rate_blocks():
    result = evaluate_commission(
        offer(displayed_total_rate_pct=verified(8), displayed_payout_mxn=verified(120)),
        now=NOW,
    )
    assert result["basis"] == "RATE_PAYOUT_CONFLICT"
    assert result["offered_per_sale_mxn"] is None


def test_invalid_listing_and_negative_rate_do_not_get_false_payout():
    with pytest.raises(ValueError):
        evaluate_commission(offer(item_id="CATALOG123"), now=NOW)
    bad = offer(displayed_total_rate_pct=verified(-5))
    assert evaluate_commission(bad, now=NOW)["offered_per_sale_mxn"] is None


def test_no_public_api_rate_does_not_become_affiliate_commission():
    unknown = offer(
        category_rate_pct=EvidenceValue.inferred(10, source="public affiliate homepage"),
        displayed_total_rate_pct=EvidenceValue.unknown(),
    )
    result = evaluate_commission(unknown, now=NOW)
    assert result["offered_per_sale_mxn"] is None
    assert result["production_decision"] == "NEEDS_DATA"


def test_summary_counts_offers_and_missing_data_without_guesswork():
    report = summarize_commissions([
        offer(displayed_payout_mxn=verified(120)),
        offer(displayed_total_rate_pct=verified(8)),
        offer(),
    ], now=NOW)
    assert report["offers_checked"] == 3
    assert report["offers_with_displayed_verified_amount"] == 1
    assert report["offers_with_calculated_estimate"] == 1
    assert report["offers_without_payout"] == 1

def test_mxn_must_be_proven_before_reporting_a_per_sale_amount():
    no_currency = offer(displayed_payout_mxn=verified(120), currency=EvidenceValue.unknown())
    result = evaluate_commission(no_currency, now=NOW)
    assert result["basis"] == "CURRENCY_UNVERIFIED_OR_NON_MXN"
    assert result["offered_per_sale_mxn"] is None
    usd = offer(displayed_payout_mxn=verified(120), currency=verified("USD"))
    assert evaluate_commission(usd, now=NOW)["offered_per_sale_mxn"] is None
