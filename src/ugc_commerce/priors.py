from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CommercePerformancePriorV1(BaseModel):
    """Local mirror of MIO's evidence-backed first-party performance prior."""

    schema_version: Literal["1.0"] = "1.0"
    prior_id: str
    platform: str
    window_hours: Literal[24, 72, 168, 720]
    filters: dict[str, str] = Field(default_factory=dict)
    sample_size: int = Field(ge=1)
    ctr_median: float | None = Field(default=None, ge=0, le=1)
    cvr_median: float | None = Field(default=None, ge=0, le=1)
    ctr_stdev: float | None = Field(default=None, ge=0)
    cvr_stdev: float | None = Field(default=None, ge=0)
    classification: Literal["WIN", "PROMISING", "INCONCLUSIVE", "LOSE"]
    confidence_score: int = Field(ge=0, le=100)
    source_refs: list[str] = Field(min_length=1)
    causal_claim: Literal[False] = False
    generated_at: datetime

    def usable(self, *, min_sample_size: int = 5, min_confidence: int = 55) -> bool:
        return (
            self.classification in {"WIN", "PROMISING"}
            and self.sample_size >= min_sample_size
            and self.confidence_score >= min_confidence
            and self.ctr_median is not None
            and self.cvr_median is not None
        )


def normalize_platform(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_")
    aliases = {
        "tiktok_shop": "tiktok",
        "tiktokshop": "tiktok",
        "tik_tok": "tiktok",
    }
    return aliases.get(normalized, normalized)


def prior_matches_platform(prior: CommercePerformancePriorV1, platform: str) -> bool:
    return normalize_platform(prior.platform) == normalize_platform(platform)
