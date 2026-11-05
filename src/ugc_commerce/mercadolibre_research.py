"""Normalize verified Mercado Libre catalogue offers without changing the production engine.

This is a pure adapter for the output of the separate LUZYA Mercado Libre Research
MCP tool. It makes no HTTP requests, assumes no affiliate authorization, and never
promotes unknown fields to verified evidence.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from typing import Any, Mapping

from .offers import EvidenceStatus, EvidenceValue, ProductOfferSnapshot

_ITEM_ID = re.compile(r"^MLM\d{1,20}$")
_OFFER_STATES = {"available", "unavailable", "not_requested"}


def _verified_field(record: Any) -> bool:
    return (
        isinstance(record, Mapping)
        and record.get("status") == "VERIFIED"
        and record.get("value") is not None
    )


def _evidence(record: Any) -> EvidenceValue:
    """Preserve provenance and observations; unknown must stay unknown."""
    if not isinstance(record, Mapping):
        return EvidenceValue.unknown()
    source = record.get("source")
    source = source if isinstance(source, str) and source.startswith("https://") else None
    status = record.get("status", "UNKNOWN")
    value = record.get("value")
    if value is None or status not in {s.value for s in EvidenceStatus}:
        return EvidenceValue.unknown(source=source)
    observed = record.get("observed_at")
    verified_at = None
    if status == "VERIFIED" and isinstance(observed, str):
        try:
            verified_at = datetime.fromisoformat(observed.replace("Z", "+00:00"))
        except ValueError:
            pass
    return EvidenceValue(
        value=value,
        status=EvidenceStatus(status),
        source=source,
        verified_at=verified_at,
    )


def convert_catalog_offer(
    catalog: Mapping[str, Any],
    offer: Mapping[str, Any],
    *,
    seller: Mapping[str, Any] | None = None,
) -> ProductOfferSnapshot | None:
    """Create a seller listing snapshot only when the catalogue title is verified.

    This intentionally leaves affiliate links, commissions, stock, rights, ratings,
    and sales UNKNOWN. A catalogue offer is not proof of affiliate eligibility.
    """
    if catalog.get("kind") != "catalog" or offer.get("kind") != "item":
        return None
    item_id = offer.get("id")
    catalog_fields = catalog.get("fields") or {}
    offer_fields = offer.get("fields") or {}
    title_record = catalog_fields.get("title")
    if (
        not isinstance(item_id, str)
        or not _ITEM_ID.fullmatch(item_id)
        or not _verified_field(title_record)
        or not isinstance(title_record["value"], str)
        or not title_record["value"].strip()
    ):
        return None

    price = _evidence(offer_fields.get("price"))
    currency = _evidence(offer_fields.get("currency"))
    seller_id = _evidence(offer_fields.get("seller_id"))
    seller_name = None
    if isinstance(seller, Mapping):
        fields = seller.get("fields") or {}
        nickname = fields.get("nickname")
        if (
            _verified_field(nickname)
            and str(seller.get("id")) == str(seller_id.value)
        ):
            seller_name = str(nickname["value"])

    sources = []
    for source in (
        catalog.get("source"),
        offer.get("source"),
        price.source,
        currency.source,
    ):
        if isinstance(source, str) and source.startswith("https://") and source not in sources:
            sources.append(source)

    return ProductOfferSnapshot(
        platform="mercadolibre",
        market="MX",
        product_id=item_id,
        title=title_record["value"].strip(),
        seller_name=seller_name,
        # API evidence endpoint is not a public commercial listing/affiliate URL.
        source_url=offer.get("source") if isinstance(offer.get("source"), str) else None,
        price_amount=price,
        currency=currency,
        # An item-level quantity is not verified by a catalogue offer.
        stock_status=EvidenceValue.unknown(),
        category=str(catalog_fields.get("category_id", {}).get("value"))
        if _verified_field(catalog_fields.get("category_id")) else None,
        commercial_rights_status="pending",
        source_provenance=sources,
    )


def summarize_candidate_batch(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Explain commercial coverage separately from catalogue retrieval success.

    A 30/30 catalogue response must not be reported as 30 commercially verified
    product offers. Missing or blocked offers are retained as missing evidence.
    """
    entries = payload.get("candidates") or []
    if not isinstance(entries, list):
        raise ValueError("candidates must be a list")

    statuses: Counter[str] = Counter()
    failure_codes: Counter[str] = Counter()
    offers_seen = 0
    priced_offers = 0
    seller_identified = 0
    snapshots_created = 0

    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        status = str(entry.get("offers_status", "not_requested"))
        statuses[status if status in _OFFER_STATES else "unknown"] += 1
        err = entry.get("offers_error")
        if isinstance(err, Mapping) and err.get("code"):
            failure_codes[str(err["code"])] += 1
        offers = entry.get("offers") or []
        if not isinstance(offers, list):
            continue
        for offer in offers:
            if not isinstance(offer, Mapping):
                continue
            offers_seen += 1
            fields = offer.get("fields") or {}
            if _verified_field(fields.get("price")) and _verified_field(fields.get("currency")):
                priced_offers += 1
            if _verified_field(fields.get("seller_id")):
                seller_identified += 1
            if convert_catalog_offer(entry, offer) is not None:
                snapshots_created += 1

    return {
        "site_id": payload.get("site_id"),
        "catalogs_returned": len(entries),
        "catalogues_queried_for_offers": statuses["available"] + statuses["unavailable"],
        "catalogues_with_offers": statuses["available"],
        "catalogues_without_offer_lookup": statuses["not_requested"],
        "offer_lookup_failures": dict(failure_codes),
        "offers_returned": offers_seen,
        "offers_with_verified_price_and_currency": priced_offers,
        "offers_with_verified_seller_id": seller_identified,
        "offer_snapshots_created": snapshots_created,
        "affiliate_commission_verified": 0,
        "production_approval": "NEEDS_DATA",
        "note": "No affiliate eligibility, commission, stock, rights or return rate is confirmed by this batch.",
    }
