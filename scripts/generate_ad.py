#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ugc_commerce.domain import Approval, UGCPlan
from ugc_commerce.higgsfield import HiggsfieldClient


def load(path: Path, model):
    return model.model_validate_json(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate approved UGC scenes sequentially with Higgsfield")
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--approval", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    plan = load(args.plan, UGCPlan)
    approval = load(args.approval, Approval)
    files = HiggsfieldClient().execute_plan(plan, approval, args.out)
    for path in files:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
