"""product_scout_score — codifies the UGC Affiliate Factory 100-point scoring rubric.

Source of truth for the rubric (read-only reference, not imported or copied as
code — cano-ai-command-center is external and read-only):
    cano-ai-command-center/01-offices/ugc-affiliate/.claude/agents/ugc-product-scout.md

That rubric exists today only as prose instructions for a Claude agent — the
scoring *math* itself was not codified anywhere as a testable function. This
module is that missing implementation: pure, deterministic, no network calls,
operating only on already-structured inputs.

Six axes (per the source doc):
  1. Comisión estimada           0-25 pts (tiered by MXN commission)
  2. Potencial visual             0-20 pts (3 yes/no sub-checks: 10+5+5)
  3. Fit con el canal              0-20 pts (one of 4 tiers)
  4. Potencial viral               0-15 pts (3 yes/no sub-checks: 5+5+5)
  5. Riesgo                     -10-0 pts (penalty only, worst applicable tier)
  6. Facilidad de producción      0-10 pts (3 yes/no sub-checks: 5+3+2)

Note on the "100 puntos" name: the source doc's own per-axis point values sum
to a 90-point maximum (25+20+20+15+10, since riesgo never adds, only
subtracts) — not 100. This module reproduces the documented per-axis values
exactly rather than inventing extra points to force the total to 100; the
name is kept only because it's what the source system and its agents call it.

Decision thresholds (per the source doc's "Reglas de comportamiento"):
  score >= 60        -> PROCEDE
  55 <= score < 60    -> EN ESPERA
  score < 55          -> RECHAZADO
  has_medical_claims  -> RECHAZADO regardless of score (hard override, no
                         exceptions per source doc: "Nunca aprobar productos
                         con claims médicos sin importar el score")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ScoutDecision(StrEnum):
    PROCEDE = "PROCEDE"
    EN_ESPERA = "EN_ESPERA"
    RECHAZADO = "RECHAZADO"


class ChannelFitTier(StrEnum):
    PERFECT = "perfect"       # "Encaja perfectamente con el nicho" -> 20
    GOOD = "good"              # "Encaja bastante bien" -> 12
    SO_SO = "so_so"            # "Encaja más o menos" -> 5
    NONE = "none"              # "No encaja" -> 0


_CHANNEL_FIT_POINTS: dict[ChannelFitTier, int] = {
    ChannelFitTier.PERFECT: 20,
    ChannelFitTier.GOOD: 12,
    ChannelFitTier.SO_SO: 5,
    ChannelFitTier.NONE: 0,
}


@dataclass(frozen=True)
class ProductScoutInput:
    """Structured, already-judged inputs to the rubric.

    Callers (an LLM agent, a human, or a future automated estimator) are
    responsible for producing these judgments from raw product data — this
    function only applies the point math, it does not infer visual appeal,
    channel fit, virality, or risk from a URL or description.
    """

    # 1. Comisión estimada (MXN)
    commission_mxn: float

    # 2. Potencial visual (3 yes/no sub-checks)
    understandable_in_3s: bool
    has_clear_visual_change: bool
    is_photogenic: bool

    # 3. Fit con el canal
    channel_fit: ChannelFitTier

    # 4. Potencial viral (3 yes/no sub-checks)
    solves_specific_common_pain: bool
    is_impulse_priced: bool  # accessible price, <$500 MXN ideal
    is_trending: bool

    # 5. Riesgo (apply the single worst-applicable tier; None = sin riesgo)
    requires_medical_claims: bool = False
    requires_physical_demo_without_vto: bool = False
    has_known_platform_restrictions: bool = False

    # 6. Facilidad de producción (3 yes/no sub-checks)
    has_good_url_images: bool = False
    no_real_action_video_required: bool = False
    simple_avatar_and_script: bool = False


@dataclass(frozen=True)
class ProductScoutScore:
    commission_points: int
    visual_points: int
    channel_fit_points: int
    viral_points: int
    risk_points: int  # <= 0
    production_ease_points: int
    total: int
    decision: ScoutDecision
    reasons: list[str] = field(default_factory=list)


def _commission_points(commission_mxn: float) -> int:
    if commission_mxn >= 150:
        return 25
    if commission_mxn >= 80:
        return 20
    if commission_mxn >= 40:
        return 15
    if commission_mxn >= 20:
        return 5
    return 0


def _visual_points(inp: ProductScoutInput) -> int:
    return (
        (10 if inp.understandable_in_3s else 0)
        + (5 if inp.has_clear_visual_change else 0)
        + (5 if inp.is_photogenic else 0)
    )


def _viral_points(inp: ProductScoutInput) -> int:
    return (
        (5 if inp.solves_specific_common_pain else 0)
        + (5 if inp.is_impulse_priced else 0)
        + (5 if inp.is_trending else 0)
    )


def _risk_points(inp: ProductScoutInput) -> tuple[int, list[str]]:
    """Worst-applicable single penalty, per the source doc's risk table.

    The source doc lists the risk axis as a single-tier table (not additive
    sub-checks like the other axes), so a product with multiple risk flags
    still only takes the worst applicable penalty, not their sum.
    """
    reasons: list[str] = []
    if inp.requires_medical_claims:
        reasons.append("riesgo: claims médicos necesarios (-10)")
        return -10, reasons
    if inp.requires_physical_demo_without_vto:
        reasons.append("riesgo: requiere producto físico sin Virtual Try On (-5)")
        return -5, reasons
    if inp.has_known_platform_restrictions:
        reasons.append("riesgo: restricciones conocidas en plataforma (-5)")
        return -5, reasons
    return 0, reasons


def _production_ease_points(inp: ProductScoutInput) -> int:
    return (
        (5 if inp.has_good_url_images else 0)
        + (3 if inp.no_real_action_video_required else 0)
        + (2 if inp.simple_avatar_and_script else 0)
    )


def score_product(inp: ProductScoutInput) -> ProductScoutScore:
    """Apply the UGC Affiliate Factory 100-point rubric to structured inputs."""
    commission_points = _commission_points(inp.commission_mxn)
    visual_points = _visual_points(inp)
    channel_fit_points = _CHANNEL_FIT_POINTS[inp.channel_fit]
    viral_points = _viral_points(inp)
    risk_points, reasons = _risk_points(inp)
    production_ease_points = _production_ease_points(inp)

    total = (
        commission_points
        + visual_points
        + channel_fit_points
        + viral_points
        + risk_points
        + production_ease_points
    )

    if inp.requires_medical_claims:
        # Hard override: "Nunca aprobar productos con claims médicos sin
        # importar el score" — RECHAZADO regardless of the numeric total.
        decision = ScoutDecision.RECHAZADO
        reasons.append("RECHAZADO por override de claims médicos (regla dura, sin excepciones)")
    elif total >= 60:
        decision = ScoutDecision.PROCEDE
    elif total >= 55:
        decision = ScoutDecision.EN_ESPERA
        reasons.append("score 55-59: EN ESPERA, sugerir mejora (ej. mejor comisión) antes de producir")
    else:
        decision = ScoutDecision.RECHAZADO

    return ProductScoutScore(
        commission_points=commission_points,
        visual_points=visual_points,
        channel_fit_points=channel_fit_points,
        viral_points=viral_points,
        risk_points=risk_points,
        production_ease_points=production_ease_points,
        total=total,
        decision=decision,
        reasons=reasons,
    )
