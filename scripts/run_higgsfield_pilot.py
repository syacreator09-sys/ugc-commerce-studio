#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ugc_commerce.domain import Approval, ProductManifest, UGCProfile
from ugc_commerce.higgsfield import HiggsfieldClient
from ugc_commerce.planner import build_plan


def load(path: Path, model):
    return model.model_validate_json(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--workflow", choices=["marketing_studio", "direct_scene"], default="marketing_studio")
    parser.add_argument("--mode", default="ugc")
    parser.add_argument("--model", default="kling3_0")
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("storage/higgsfield-pilot"))
    args = parser.parse_args()

    product = load(args.product, ProductManifest)
    profile = load(args.profile, UGCProfile)
    plan = build_plan(product, profile, workflow=args.workflow, mode=args.mode, model=args.model)
    args.output.mkdir(parents=True, exist_ok=True)
    plan_path = args.output / "plan.json"
    plan_path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")

    print(json.dumps({
        "plan": str(plan_path),
        "scope_id": plan.scope_id,
        "workflow": plan.workflow,
        "mode": plan.mode,
        "scenes": len(plan.scenes),
        "paid_generation": not args.plan_only,
    }, indent=2))

    if args.plan_only:
        return 0
    if not args.approval:
        raise SystemExit("--approval is required for paid generation")

    approval = load(args.approval, Approval)
    scene_files = HiggsfieldClient().execute_plan(plan, approval, args.output / "scenes")
    print(json.dumps({"scenes": [str(path) for path in scene_files], "auto_publish": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
