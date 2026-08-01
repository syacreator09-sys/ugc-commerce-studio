from __future__ import annotations

from .domain import ProductManifest, Scene, UGCPlan, UGCProfile
from .normalizer import normalize_spoken


def build_scenes(product: ProductManifest, profile: UGCProfile) -> list[Scene]:
    benefit = product.verified_benefits[0] if product.verified_benefits else "resuelve una necesidad concreta"
    natural = [
        f"Pensé que {product.title} era otro producto más, pero me sorprendió.",
        f"Lo probé porque {benefit}.",
        "Lo que más me gustó fue lo fácil que resulta entenderlo y usarlo.",
        profile.cta,
    ]
    goals = ["hook", "context", "verified_benefit", "cta"]
    vibes = ["curious and natural", "honest and conversational", "confident but not exaggerated", "friendly recommendation"]
    visuals = [
        "selfie opening with product visible",
        "presenter shows the registered product naturally",
        "close product demonstration without inventing functions",
        "direct eye contact with verified product card added later",
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
    if not product.verified_benefits:
        raise ValueError("at least one verified benefit is required")
    return UGCPlan.create(
        workflow=workflow,
        mode=mode,
        model=model,
        product=product,
        profile=profile,
        scenes=build_scenes(product, profile),
    )
