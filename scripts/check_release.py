#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

REQUIRED = [
    "README.md",
    "SKILL.md",
    "AGENTS.md",
    "CLAUDE.md",
    "LICENSE",
    "pyproject.toml",
    "Makefile",
    "config/policies.json",
    "config/higgsfield.json",
    "scripts/doctor.py",
    "scripts/generate_ad.py",
    "scripts/transcribe_correct.py",
    "scripts/build_composition.py",
    "src/ugc_commerce/cli.py",
    "src/ugc_commerce/higgsfield.py",
    "tests/test_planner.py",
]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    missing = [path for path in REQUIRED if not (root / path).exists()]
    policies = json.loads((root / "config/policies.json").read_text(encoding="utf-8"))
    unsafe = [
        key for key in ("auto_publish", "auto_activate_ads", "auto_scale_budget")
        if policies.get(key) is not False
    ]
    if missing or unsafe:
        print(json.dumps({"status": "FAIL", "missing": missing, "unsafe": unsafe}, indent=2))
        return 1
    print(json.dumps({"status": "PASS", "required_files": len(REQUIRED), "unsafe": []}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
