#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from ugc_commerce.domain import ProductManifest, UGCProfile
from ugc_commerce.planner import build_plan


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    product = ProductManifest.model_validate_json((root / "examples/product.json").read_text(encoding="utf-8"))
    profile = UGCProfile.model_validate_json((root / "examples/profile.json").read_text(encoding="utf-8"))
    plan = build_plan(product, profile)
    output = root / "storage/demo-plan.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "PLAN_READY",
        "scope_id": plan.scope_id,
        "scenes": len(plan.scenes),
        "paid_generation": False,
        "output": str(output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
