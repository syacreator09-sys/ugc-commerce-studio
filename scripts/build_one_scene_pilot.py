#!/usr/bin/env python3
"""Derive a one-scene pilot plan from an existing approved-product UGCPlan.

Changes scope_id deterministically. Does NOT create Approval, spend credits or
contact Higgsfield. Requires a separately explicit human approval for new scope.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ugc_commerce.domain import UGCPlan
from ugc_commerce.sources import validate_product


def make_pilot(master: UGCPlan, index: int = 1) -> UGCPlan:
    if len(master.scenes) != 6:
        raise ValueError("Parent must be a six-scene commercial plan")
    if [s.index for s in master.scenes] != list(range(1, 7)):
        raise ValueError("Parent scene indices must be 1..6")
    if any(s.duration_seconds != 5 for s in master.scenes):
        raise ValueError("Parent six-scene preset must have five-second scenes")
    if index not in range(1, 7):
        raise ValueError("Scene index must be 1..6")
    validate_product(master.product)
    selected = master.scenes[index - 1].model_copy(update={"index": 1})
    matrix = dict(master.creative_matrix)
    matrix["pilot_from_six_scene_plan"] = {
        "parent_scope_id": master.scope_id,
        "source_scene_index": index,
        "pilot_only": True,
    }
    pilot = UGCPlan.create(
        workflow=master.workflow,
        mode=master.mode,
        model=master.model,
        product=master.product,
        profile=master.profile,
        opportunity=master.opportunity,
        creative_matrix=matrix,
        scenes=[selected],
    )
    if pilot.scope_id == master.scope_id:
        raise ValueError("Pilot must get a distinct scope_id")
    return pilot


def main() -> int:
    p = argparse.ArgumentParser(description="Offline one-scene pilot from canonical six-scene plan")
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--scene-index", type=int, default=1)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    try:
        parent = UGCPlan.model_validate_json(args.plan.read_text(encoding="utf-8"))
        pilot = make_pilot(parent, args.scene_index)
    except (OSError, ValueError) as error:
        p.exit(2, f"Pilot blocked: {error}\n")
    if args.output.exists():
        p.exit(2, "Output already exists; refusing to overwrite an immutable plan\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(pilot.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PILOT_PLAN_READY_APPROVAL_REQUIRED",
        "parent_scope_id": parent.scope_id,
        "pilot_scope_id": pilot.scope_id,
        "scenes": len(pilot.scenes),
        "premium_approved": False,
        "actual_cost_usd": 0,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
