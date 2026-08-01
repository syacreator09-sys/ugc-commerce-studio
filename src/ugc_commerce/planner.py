from __future__ import annotations

from .domain import ProductManifest, Scene, UGCPlan, UGCProfile
from .intelligence import creative_matrix, opportunity_score
from .normalizer import normalize_spoken


def build_scenes(product: ProductManifest, profile: UGCProfile) -> list[Scene]:
    benefit = product.verified_benefits[0] if product.verified_benefits else "resuelve una necesidad concreta"
    natural = [
        f"Pensé que {product.title} era otro producto más, pero me sorprendió.",
        f"Lo probé porque {benefit}.",
        "Te enseño cómo se ve y qué incluye, sin exagerar lo que hace.",
        "Lo que más me gustó fue lo fácil que resulta entenderlo y usarlo.",
        profile.cta,
    ]
    goals = ["hook", "context", "demonstration", "verified_benefit", "cta"]
    vibes = [
        "curious and natural",
        "honest and conversational",
        "clear and practical",
        "confident but not exaggerated",
        "friendly recommendation",
    ]
    visuals = [
        "selfie opening with registered product visible",
        "presenter explains the verified problem or use case",
        "presenter shows product shape and included elements without inventing functions",
        "close product demonstration based only on verified benefits",
        "direct eye contact; exact product card and price are added locally later",
    ]
    return [
        Scene(
            index=index,
            goal=goal,
            natural_text=text,
            spoken_text=normalize_spoken(text),
            caption_text=text,
            vibe=vibe,
            visual_direction=visual,
        )
        for index, (goal, text, vibe, visual) in enumerate(zip(goals, natural, vibes, visuals), start=1)
    ]


def build_plan(
    product: ProductManifest,
    profile: UGCProfile,
    *,
    workflow: str = "marketing_studio",
    mode: str = "ugc",
    model: str = "kling3_0",
) -> UGCPlan:
    if product.commercial_rights_status != "approved":
        raise ValueError("commercial rights must be approved before planning")
    if product.availability not in {"available", "in_stock"}:
        raise ValueError("product must be available before planning")
    if not product.verified_benefits:
        raise ValueError("at least one verified benefit is required")
    if workflow == "direct_scene" and not product.media_assets:
        raise ValueError("direct_scene requires at least one authorized start image")

    opportunity = opportunity_score(product)
    if opportunity["recommendation"] == "REJECT":
        raise ValueError("product opportunity score rejected the campaign")

    return UGCPlan.create(
        workflow=workflow,
        mode=mode,
        model=model,
        product=product,
        profile=profile,
        opportunity=opportunity,
        creative_matrix=creative_matrix(product),
        scenes=build_scenes(product, profile),
    )
