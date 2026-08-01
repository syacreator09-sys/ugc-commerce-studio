#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def command_ok(command: list[str]) -> bool:
    try:
        return subprocess.run(command, capture_output=True, text=True, timeout=30).returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/user-config.json")
    args = parser.parse_args()

    checks = {
        "python": True,
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "ffprobe": shutil.which("ffprobe") is not None,
        "higgsfield_cli": shutil.which("higgsfield") is not None,
        "higgsfield_authenticated": command_ok(["higgsfield", "account", "status", "--json"]),
        "hyperframes": command_ok(["npx", "hyperframes", "--version"]),
        "config_exists": Path(args.config).exists(),
    }
    print(json.dumps(checks, indent=2))
    required = checks["ffmpeg"] and checks["ffprobe"]
    return 0 if required else 1


if __name__ == "__main__":
    raise SystemExit(main())
