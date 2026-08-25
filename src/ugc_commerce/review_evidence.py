from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CommerceReviewEvidenceV1(BaseModel):
    """Review-derived market evidence. This contract intentionally has no claim fields."""

    schema_version: Literal["1.0"] = "1.0"
    evidence_id: str
    product_ref: str
    sample_size: int = Field(ge=0)
    average_rating: float | None = Field(default=None, ge=0, le=5)
    positive_themes: list[str] = Field(default_factory=list)
    negative_themes: list[str] = Field(default_factory=list)
    recurring_complaints: list[str] = Field(default_factory=list)
    unmet_needs: list[str] = Field(default_factory=list)
    quality_expectations: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    provenance: list[str] = Field(default_factory=list)
    observed_at: datetime | None = None
    generated_at: datetime


class ReviewCreativeSignals(BaseModel):
    angle_candidates: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    provenance: list[str] = Field(default_factory=list)


def derive_review_creative_signals(evidence: CommerceReviewEvidenceV1) -> ReviewCreativeSignals:
    """Turn review evidence into creative research signals, never product claims."""
    candidates: list[str] = []
    for label, values in (
        ("complaint", evidence.recurring_complaints),
        ("unmet_need", evidence.unmet_needs),
        ("quality_expectation", evidence.quality_expectations),
        ("negative_theme", evidence.negative_themes),
        ("positive_theme", evidence.positive_themes),
    ):
        for value in values:
            text = str(value).strip()
            if text:
                candidates.append(f"{label}:{text}")
    return ReviewCreativeSignals(
        angle_candidates=list(dict.fromkeys(candidates)),
        evidence_refs=list(dict.fromkeys([evidence.evidence_id, *evidence.source_refs])),
        provenance=list(dict.fromkeys(evidence.provenance)),
    )
