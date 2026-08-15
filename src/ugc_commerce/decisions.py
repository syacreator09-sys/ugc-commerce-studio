from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from .confidence import ConfidenceReport
from .creative_capacity import CreativeCapacityReport
from .economics import AffiliateEconomics
from .offers import EvidenceStatus, ProductOfferSnapshot
from .product_scout_score import ProductScoutScore, ScoutDecision


class SampleDecision(StrEnum):
    SOLICITAR = "SOLICITAR"
    NO_SOLICITAR = "NO_SOLICITAR"
    NEEDS_DATA = "NEEDS_DATA"


class ProductionDecision(StrEnum):
    PROCEDE = "PROCEDE"
    EN_ESPERA = "EN_ESPERA"
    RECHAZADO = "RECHAZADO"


class DecisionReport(BaseModel):
    sample_decision: SampleDecision
    production_decision: ProductionDecision
    hard_gates: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    recommended_initial_creatives: int | str = 0


def _hard_gates(offer: ProductOfferSnapshot) -> list[str]:
    gates: list[str] = []
    if offer.requires_medical_claims:
        gates.append("medical claims require unsupported/regulated claims")
    if offer.commercial_rights_status == "rejected":
        gates.append("commercial rights rejected")
    if offer.has_blocking_platform_restrictions:
        gates.append("blocking platform restriction makes offer non-viable")
    if offer.critical_evidence_conflict:
        gates.append("critical evidence conflict")
    return gates


def decide_product(
    *,
    offer: ProductOfferSnapshot,
    economics: AffiliateEconomics,
    confidence: ConfidenceReport,
    ugc_score: ProductScoutScore,
    creative_capacity: CreativeCapacityReport,
) -> DecisionReport:
    gates = _hard_gates(offer)
    if gates:
        return DecisionReport(
            sample_decision=SampleDecision.NO_SOLICITAR,
            production_decision=ProductionDecision.RECHAZADO,
            hard_gates=gates,
            reasons=["hard gate blocks commercial scoring"],
            recommended_initial_creatives=0,
        )

    reasons: list[str] = []
    commission = economics.organic_commission_per_sale
    free_sample_verified = offer.free_sample_available.status == EvidenceStatus.VERIFIED
    free_sample_value = bool(offer.free_sample_available.value) if free_sample_verified else None

    if commission is not None and commission <= 0:
        return DecisionReport(
            sample_decision=SampleDecision.NO_SOLICITAR,
            production_decision=ProductionDecision.RECHAZADO,
            reasons=["verified affiliate commission is zero or non-positive"],
            recommended_initial_creatives=0,
        )

    if free_sample_verified and free_sample_value is False:
        sample_decision = SampleDecision.NO_SOLICITAR
        reasons.append("free sample is explicitly unavailable")
    elif free_sample_verified and free_sample_value is True:
        if confidence.score >= 70 and commission is not None and commission > 0:
            sample_decision = SampleDecision.SOLICITAR
            reasons.append("free sample plus sufficient verified economics")
        else:
            sample_decision = SampleDecision.NEEDS_DATA
            reasons.append("free sample exists but economics/data quality need verification")
    else:
        sample_decision = SampleDecision.NEEDS_DATA
        reasons.append("sample availability is unknown")

    if offer.commercial_rights_status == "pending":
        production_decision = ProductionDecision.EN_ESPERA
        reasons.append("commercial rights pending")
    elif confidence.score < 60:
        production_decision = ProductionDecision.EN_ESPERA
        reasons.append("data confidence below production threshold")
    elif commission is None:
        production_decision = ProductionDecision.EN_ESPERA
        reasons.append("organic commission is not verified/calculable")
    elif ugc_score.decision == ScoutDecision.RECHAZADO:
        production_decision = ProductionDecision.RECHAZADO
        reasons.append("legacy UGC fit score rejected product")
    elif ugc_score.decision == ScoutDecision.EN_ESPERA:
        production_decision = ProductionDecision.EN_ESPERA
        reasons.append("legacy UGC fit score is in waiting band")
    else:
        production_decision = ProductionDecision.PROCEDE
        reasons.append("verified economics, sufficient confidence and UGC fit")

    recommended = creative_capacity.recommended_initial_creatives if production_decision == ProductionDecision.PROCEDE else 0
    return DecisionReport(
        sample_decision=sample_decision,
        production_decision=production_decision,
        hard_gates=gates,
        reasons=reasons,
        recommended_initial_creatives=recommended,
    )
