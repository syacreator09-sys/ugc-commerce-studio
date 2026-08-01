from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from .domain import Approval, Scene, UGCPlan


class HiggsfieldError(RuntimeError):
    pass


class HiggsfieldClient:
    """Thin fail-closed adapter over the official Higgsfield CLI."""

    def __init__(self, *, enabled: bool | None = None, max_retries: int = 3) -> None:
        self.enabled = enabled if enabled is not None else os.getenv("HIGGSFIELD_ENABLED", "false").lower() == "true"
        self.max_retries = max_retries

    def doctor(self) -> dict[str, Any]:
        version = self._run(["higgsfield", "version"], allow_disabled=True)
        account = self._run(["higgsfield", "account", "status", "--json"], allow_disabled=True)
        return {
            "enabled": self.enabled,
            "cli_installed": version.returncode == 0,
            "authenticated": account.returncode == 0,
            "status": "CONNECTED" if self.enabled and account.returncode == 0 else "NOT_CONNECTED",
        }

    def execute_plan(self, plan: UGCPlan, approval: Approval, output_dir: Path) -> list[Path]:
        if not self.enabled:
            raise HiggsfieldError("Higgsfield is disabled; set HIGGSFIELD_ENABLED=true after authentication")
        if approval.scope_id != plan.scope_id:
            raise HiggsfieldError("approval scope does not match immutable plan scope")

        output_dir.mkdir(parents=True, exist_ok=True)
        results: list[Path] = []
        for scene in plan.scenes:
            target = output_dir / f"scene-{scene.index}.mp4"
            evidence = output_dir / f"scene-{scene.index}.json"
            if target.exists() and evidence.exists():
                results.append(target)
                continue
            command = self._command_for_scene(plan, scene)
            payload = self._run_json_with_retry(command)
            url = self._extract_result_url(payload)
            self._download(url, target)
            evidence.write_text(json.dumps({"command": command, "response": payload}, indent=2), encoding="utf-8")
            results.append(target)
            time.sleep(8)
        return results

    def _command_for_scene(self, plan: UGCPlan, scene: Scene) -> list[str]:
        prompt = build_prompt(plan, scene)
        if plan.workflow == "direct_scene":
            if not plan.product.media_assets:
                raise HiggsfieldError("direct_scene requires a start image in product.media_assets")
            return [
                "higgsfield", "generate", "create", plan.model,
                "--prompt", prompt,
                "--aspect_ratio", "9:16",
                "--duration", str(scene.duration_seconds),
                "--start-image", plan.product.media_assets[0],
                "--wait", "--json",
            ]

        return [
            "higgsfield", "generate", "create", "marketing_studio_video",
            "--prompt", prompt,
            "--mode", plan.mode,
            "--aspect_ratio", "9:16",
            "--duration", str(scene.duration_seconds),
            "--resolution", "720p",
            "--generate_audio", "true",
            "--wait", "--json",
        ]

    def _run_json_with_retry(self, command: list[str]) -> Any:
        last_error = "unknown error"
        for attempt in range(1, self.max_retries + 1):
            result = self._run(command)
            if result.returncode == 0:
                return json.loads(result.stdout)
            last_error = (result.stderr or result.stdout).strip()
            if attempt < self.max_retries:
                time.sleep(attempt * 30)
        raise HiggsfieldError(f"Higgsfield failed after {self.max_retries} attempts: {last_error[:500]}")

    def _run(self, command: list[str], *, allow_disabled: bool = False) -> subprocess.CompletedProcess[str]:
        if not allow_disabled and not self.enabled:
            raise HiggsfieldError("Higgsfield is disabled")
        try:
            return subprocess.run(command, capture_output=True, text=True, timeout=1800, check=False)
        except FileNotFoundError:
            return subprocess.CompletedProcess(command, 127, "", "higgsfield CLI not found")

    @staticmethod
    def _extract_result_url(payload: Any) -> str:
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            for key in ("result_url", "url", "output_url"):
                value = item.get(key) if isinstance(item, dict) else None
                if value:
                    return str(value)
        raise HiggsfieldError("result URL not found in CLI response")

    @staticmethod
    def _download(url: str, target: Path) -> None:
        from urllib.request import urlretrieve
        urlretrieve(url, target)


def build_prompt(plan: UGCPlan, scene: Scene) -> str:
    return (
        f'The presenter speaks this dialogue with natural, accurate lip-sync and reads it exactly as written: '
        f'"{scene.spoken_text}". '
        f'Language: Latin American Spanish, neutral Mexican/Colombian accent. '
        f'Performance: {scene.vibe}; natural selfie UGC, direct eye contact, subtle gestures, no theatrical behavior. '
        f'Product: {plan.product.title}. Use only registered or supplied product references. '
        f'Preserve shape, color, packaging and brand identity. Do not invent labels, prices, accessories, effects or functions. '
        f'Scene goal: {scene.goal}. Direction: {scene.visual_direction}. Vertical 9:16.'
    )
