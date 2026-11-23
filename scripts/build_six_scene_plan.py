#!/usr/bin/env python3
"""Convert an individually reviewed six-beat script into the EXISTING UGCPlan.

This tool only prepares a canonical plan. It cannot approve premium spend, invoke
Higgsfield, synthesize fictional product claims or publish.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from ugc_commerce.domain import ProductManifest, Scene, UGCPlan, UGCProfile
from ugc_commerce.planner import build_plan
from ugc_commerce.sources import ProductValidationError

BEATS = ("hook", "problem", "product", "demonstration", "benefit", "cta")
BANNED_TESTIMONIALS = ("lo probé", "me funcionó", "yo lo uso", "lo compré",
                       "se me quitó", "me curó", "lo recomiendo porque lo usé")


def canonical_plan(script_file: Path, product_file: Path, profile_file: Path,
                   *, approved_script_sha256: str, reviewed_by: str,
                   workflow: str = "direct_scene", model: str = "kling3_0",
                   mode: str = "ugc") -> UGCPlan:
    if not re.fullmatch(r"[0-9a-fA-F]{64}", approved_script_sha256):
        raise ValueError("Expected an exact SHA-256 for reviewed script bytes")
    if not reviewed_by.strip():
        raise ValueError("A named human script reviewer is required")
    script_raw = script_file.read_bytes()
    digest = hashlib.sha256(script_raw).hexdigest()
    if digest.lower() != approved_script_sha256.lower():
        raise ValueError("Script changed since its creative review (SHA-256 mismatch)")
    script = json.loads(script_raw)
    if not isinstance(script, dict):
        raise ValueError("Script root must be an object")
    if script.get("status") != "APPROVED_FOR_PRODUCTION" or script.get("rights_status") != "APPROVED":
        raise ValueError("Approved script and rights required; fictional draft cannot be promoted")
    if script.get("source_kind") != "VERIFIED_PRODUCT":
        raise ValueError("FICTIONAL_DEMO cannot become a paid production plan")
    if script.get("premium_approval") is not False or script.get("publish_approved") is not False:
        raise ValueError("Script must never serve as generation/publishing approval")
    if script.get("language") != "es-LATAM":
        raise ValueError("Expected es-LATAM reviewed dialogue")
    product = ProductManifest.model_validate_json(product_file.read_text(encoding="utf-8"))
    profile = UGCProfile.model_validate_json(profile_file.read_text(encoding="utf-8"))
    if profile.language != "es-LATAM":
        raise ValueError("UGCProfile must use es-LATAM for this preset")
    if not script.get("campaign_id"):
        raise ValueError("Missing campaign_id")
    # Use canonical product guards, economics and opportunity scoring. Do not
    # create another ProductManifest or parallel UGC planning system.
    baseline = build_plan(product, profile, workflow=workflow, mode=mode, model=model)
    if baseline.opportunity["recommendation"] not in {"TEST_UGC", "PREMIUM_PRODUCTION"}:
        raise ValueError("Product opportunity not cleared for production")
    source_scenes = script.get("scenes")
    if not isinstance(source_scenes, list) or len(source_scenes) != 6:
        raise ValueError("Expected exactly six reviewed scenes")
    scenes = []
    searchable = []
    for i, item in enumerate(source_scenes):
        if not isinstance(item, dict) or item.get("beat") != BEATS[i]:
            raise ValueError(f"Invalid scene/beat at index {i + 1}")
        if item.get("start") != i * 5 or item.get("end") != (i + 1) * 5:
            raise ValueError(f"Expected contiguous five-second scene {i + 1}")
        if item.get("scene_id") != f"{script['campaign_id']}-s{i + 1:02}":
            raise ValueError("Scene ID does not match canonical commercial export")
        for key in ("natural_text", "spoken_text", "caption_text", "visual_direction"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f"Missing nonempty {key} in scene {i + 1}")
        spoken = item["spoken_text"].strip()
        natural = item["natural_text"].strip()
        searchable.append(spoken.casefold())
        if any(word in spoken.casefold() for word in BANNED_TESTIMONIALS):
            raise ValueError("Unverified personal experience language blocked")
        if any(claim.casefold() in spoken.casefold() or claim.casefold() in natural.casefold()
               for claim in product.prohibited_claims if claim.strip()):
            raise ValueError("Prohibited product claim in creative script")
        if len(spoken.split()) > 20:
            raise ValueError(f"Speech too dense for five-second scene {i + 1}")
        scenes.append(Scene(
            index=i + 1, goal=BEATS[i], natural_text=natural,
            spoken_text=spoken, caption_text=item["caption_text"].strip(),
            vibe="natural and understated, Latin American Spanish",
            visual_direction=item["visual_direction"].strip(),
            duration_seconds=5,
        ))
    # Avoid accidentally producing a different real product with the fictional
    # MODULA/NUBA/LUMO copy from a manually reclassified sample.
    brand_word = product.title.split()[-1].casefold()
    if len(brand_word) > 2 and not any(brand_word in words for words in searchable):
        raise ValueError("Real product name not present in spoken script")
    matrix = dict(baseline.creative_matrix)
    matrix["reviewed_commercial_script"] = {
        "source_campaign_id": script["campaign_id"],
        "source_sha256": digest,
        "reviewed_by": reviewed_by.strip(),
        "review_scope": "CREATIVE_ONLY_NOT_PREMIUM_APPROVAL",
    }
    return UGCPlan.create(
        workflow=workflow, mode=mode, model=model, product=product,
        profile=profile, opportunity=baseline.opportunity,
        creative_matrix=matrix, scenes=scenes,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Offline six-scene reviewed script → canonical UGCPlan")
    p.add_argument("--script", required=True, type=Path)
    p.add_argument("--product", required=True, type=Path)
    p.add_argument("--profile", required=True, type=Path)
    p.add_argument("--approved-script-sha256", required=True)
    p.add_argument("--reviewed-by", required=True)
    p.add_argument("--workflow", choices=("direct_scene", "marketing_studio"), default="direct_scene")
    p.add_argument("--model", default="kling3_0")
    p.add_argument("--mode", default="ugc")
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    try:
        plan = canonical_plan(args.script, args.product, args.profile,
                              approved_script_sha256=args.approved_script_sha256,
                              reviewed_by=args.reviewed_by,
                              workflow=args.workflow, model=args.model, mode=args.mode)
    except (ValueError, ProductValidationError, OSError, json.JSONDecodeError) as error:
        p.exit(2, f"Plan blocked: {error}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        p.exit(2, "Refusing to overwrite an existing immutable plan\n")
    args.output.write_text(plan.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "READY_FOR_SCOPE_APPROVAL", "scope_id": plan.scope_id,
                      "scenes": len(plan.scenes), "premium_approved": False,
                      "actual_cost_usd": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
