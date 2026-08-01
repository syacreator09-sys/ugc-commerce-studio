from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from .domain import Approval, Scene, UGCPlan


class HiggsfieldError(RuntimeError):
    pass


class HiggsfieldClient:
    """Fail-closed adapter over the official Higgsfield CLI."""

    def __init__(self, *, enabled: bool | None = None, max_retries: int = 3) -> None:
        self.enabled = enabled if enabled is not None else os.getenv("HIGGSFIELD_ENABLED", "false").lower() == "true"
        self.max_retries = max_retries

    def doctor(self) -> dict[str, Any]:
        version = self._run(["higgsfield", "version"], allow_disabled=True)
        account = self._run(["higgsfield", "account", "status", "--json"], allow_disabled=True)
        model = self._run(["higgsfield", "model", "get", "marketing_studio_video", "--json"], allow_disabled=True)
        authenticated = account.returncode == 0
        return {
            "enabled": self.enabled,
            "cli_installed": version.returncode == 0,
            "authenticated": authenticated,
            "marketing_studio_available": model.returncode == 0,
            "status": "CONNECTED" if self.enabled and authenticated and model.returncode == 0 else "NOT_CONNECTED",
        }

    def execute_plan(self, plan: UGCPlan, approval: Approval, output_dir: Path) -> list[Path]:
        if not self.enabled:
            raise HiggsfieldError("Higgsfield is disabled; authenticate and set HIGGSFIELD_ENABLED=true")
        if approval.scope_id != plan.scope_id:
            raise HiggsfieldError("approval scope does not match immutable plan scope")

        output_dir.mkdir(parents=True, exist_ok=True)
        product_id = self._ensure_product(plan) if plan.workflow == "marketing_studio" else None
        results: list[Path] = []
        for scene in plan.scenes:
            target = output_dir / f"scene-{scene.index}.mp4"
            evidence = output_dir / f"scene-{scene.index}.json"
            if target.exists() and evidence.exists():
                results.append(target)
                continue
            command = self._command_for_scene(plan, scene, product_id=product_id)
            payload = self._run_json_with_retry(command)
            url = self._extract_result_url(payload)
            self._download(url, target)
            evidence.write_text(
                json.dumps({"command": command, "response": payload, "scope_id": plan.scope_id}, indent=2),
                encoding="utf-8",
            )
            results.append(target)
            time.sleep(8)
        return results

    def _ensure_product(self, plan: UGCPlan) -> str:
        if plan.product.source_url:
            payload = self._run_json_with_retry([
                "higgsfield", "marketing-studio", "products", "fetch",
                "--url", str(plan.product.source_url), "--wait", "--json",
            ])
            product_id = self._extract_id(payload)
            if product_id:
                return product_id

        if not plan.product.media_assets:
            raise HiggsfieldError("marketing_studio requires product source_url or authorized product media")

        upload_ids: list[str] = []
        for asset in plan.product.media_assets:
            payload = self._run_json_with_retry([
                "higgsfield", "upload", "create", asset, "--json",
            ])
            upload_id = self._extract_id(payload)
            if not upload_id:
                raise HiggsfieldError(f"upload ID not found for product asset: {asset}")
            upload_ids.append(upload_id)

        command = [
            "higgsfield", "marketing-studio", "products", "create",
            "--title", plan.product.title,
            "--description", "; ".join(plan.product.verified_benefits),
        ]
        for upload_id in upload_ids:
            command.extend(["--image", upload_id])
        payload = self._run_json_with_retry(command + ["--json"])
        product_id = self._extract_id(payload)
        if not product_id:
            raise HiggsfieldError("product ID not found after Marketing Studio create")
        return product_id

    def _command_for_scene(self, plan: UGCPlan, scene: Scene, *, product_id: str | None) -> list[str]:
        prompt = build_prompt(plan, scene)
        if plan.workflow == "direct_scene":
            if not plan.product.media_assets:
                raise HiggsfieldError("direct_scene requires a start image in product.media_assets")
            command = [
                "higgsfield", "generate", "create", plan.model,
                "--prompt", prompt,
                "--aspect_ratio", "9:16",
                "--duration", str(scene.duration_seconds),
                "--start-image", plan.product.media_assets[0],
                "--wait", "--json",
            ]
            if plan.model == "seedance_2_0":
                command.extend(["--resolution", "720p"])
            return command

        if not product_id:
            raise HiggsfieldError("marketing_studio product ID is required")

        product_file = self._json_argument([product_id])
        command = [
            "higgsfield", "generate", "create", "marketing_studio_video",
            "--prompt", prompt,
            "--mode", plan.mode,
            "--product_ids", f"@{product_file}",
            "--aspect_ratio", "9:16",
            "--duration", str(scene.duration_seconds),
            "--resolution", "720p",
            "--generate_audio", "true",
        ]
        if plan.profile.avatar_id:
            avatar_file = self._json_argument([{"id": plan.profile.avatar_id, "type": plan.profile.avatar_type}])
            command.extend(["--avatars", f"@{avatar_file}"])
        command.extend(["--wait", "--json"])
        return command

    @staticmethod
    def _json_argument(value: Any) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        with handle:
            json.dump(value, handle)
        return handle.name

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
    def _extract_id(payload: Any) -> str | None:
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if isinstance(item, dict):
                for key in ("id", "product_id", "upload_id", "uuid"):
                    if item.get(key):
                        return str(item[key])
                for nested_key in ("product", "upload", "data"):
                    nested = item.get(nested_key)
                    if isinstance(nested, dict):
                        for key in ("id", "product_id", "upload_id", "uuid"):
                            if nested.get(key):
                                return str(nested[key])
        return None

    @staticmethod
    def _extract_result_url(payload: Any) -> str:
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if not isinstance(item, dict):
                continue
            for key in ("result_url", "url", "output_url"):
                if item.get(key):
                    return str(item[key])
            outputs = item.get("outputs") or item.get("results")
            if isinstance(outputs, list):
                for output in outputs:
                    if isinstance(output, dict) and output.get("url"):
                        return str(output["url"])
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
