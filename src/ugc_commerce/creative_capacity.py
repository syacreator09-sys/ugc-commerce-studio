from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


CreativeCount = int | Literal["10+"]


class CreativeCapacityInput(BaseModel):
    hooks: list[str] = Field(default_factory=list)
    audiences: list[str] = Field(default_factory=list)
    use_cases: list[str] = Field(default_factory=list)
    demonstrations: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    transformations: list[str] = Field(default_factory=list)
    formats: list[str] = Field(default_factory=list)
    proven_winner: bool = False


class CreativeCapacityReport(BaseModel):
    score: int = Field(ge=0, le=100)
    unique_counts: dict[str, int]
    recommended_initial_creatives: CreativeCount


def _unique(values: list[str]) -> int:
    return len({v.strip().lower() for v in values if v and v.strip()})


def assess_creative_capacity(data: CreativeCapacityInput) -> CreativeCapacityReport:
    counts = {
        "hooks": _unique(data.hooks),
        "audiences": _unique(data.audiences),
        "use_cases": _unique(data.use_cases),
        "demonstrations": _unique(data.demonstrations),
        "objections": _unique(data.objections),
        "transformations": _unique(data.transformations),
        "formats": _unique(data.formats),
    }
    score = min(counts["hooks"], 4) * 5
    score += min(counts["audiences"], 2) * 5
    score += min(counts["use_cases"], 3) * 5
    score += min(counts["demonstrations"], 3) * 5
    score += min(counts["objections"], 2) * 5
    score += min(counts["transformations"], 2) * 5
    score += min(counts["formats"], 5) * 4
    score = min(100, score)

    if data.proven_winner and score >= 70:
        count: CreativeCount = "10+"
    elif score >= 75:
        count = 5
    elif score >= 50:
        count = 3
    elif score >= 20:
        count = 1
    else:
        count = 0

    return CreativeCapacityReport(score=score, unique_counts=counts, recommended_initial_creatives=count)
