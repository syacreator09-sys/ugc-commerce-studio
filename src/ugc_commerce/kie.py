from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Literal
from urllib.request import Request, urlopen

from .domain import Approval, Scene, UGCPlan


class KieError(RuntimeError):
    pass


class KieBudgetExceededError(KieError):
    pass


# Verified directly against Kie.ai's own model pages (not third-party resellers),
# 2026-11-16. Kie.ai's own pricing cards say prices "may be updated" — re-verify
# before trusting these numbers again after `catalog_verified_at` ages.
KIE_CATALOG: dict[str, dict[str, Any]] = {
    "minimax-h3/text-to-video": {
        "display_name": "MiniMax H3 (Hailuo 03) — text to video",
        "duration_seconds_range": (4, 15),
        "resolutions": ("768p", "2k"),
        "aspect_ratios": ("21:9", "16:9", "4:3", "1:1", "3:4", "9:16"),
        "audio_always_on": True,
        "rate_usd_per_second": {"768p": 0.04, "2k": 0.065},
        "source_url": "https://kie.ai/minimax-h3",
    },
    "minimax-h3/image-to-video": {
        "display_name": "MiniMax H3 (Hailuo 03) — image to video",
        "duration_seconds_range": (4, 15),
        "resolutions": ("768p", "2k"),
        "aspect_ratios": (),  # follows the input image; no aspect_ratio parameter
        "audio_always_on": True,
        "rate_usd_per_second": {"768p": 0.04, "2k": 0.065},
        "source_url": "https://kie.ai/minimax-h3",
    },
    "minimax-h3/reference-to-video": {
        "display_name": "MiniMax H3 (Hailuo 03) — reference to video",
        "duration_seconds_range": (4, 15),
        "resolutions": ("768p", "2k"),
        "aspect_ratios": ("adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"),
        "audio_always_on": True,
        "rate_usd_per_second": {"768p": 0.04, "2k": 0.065},
        "source_url": "https://kie.ai/minimax-h3",
    },
    "kling-3.0-omni/text-to-video": {
        "display_name": "Kling O3 (Kling 3.0 Omni) — text to video",
        "duration_seconds_range": (3, 15),
        "resolutions": ("720p", "1080p", "4k"),
        "aspect_ratios": ("16:9", "9:16", "1:1"),
        "audio_always_on": False,
        "rate_usd_per_second": {
            "720p": {"no_audio": 0.0755, "audio": 0.101},
            "1080p": {"no_audio": 0.101, "audio": 0.126},
            "4k": {"no_audio": 0.3775, "audio": 0.3775},
        },
        "source_url": "https://kie.ai/kling-o3",
    },
    "kling/ai-avatar-standard": {
        "display_name": "Kling AI Avatar 2.0 — standard (720p)",
        "duration_seconds_range": (1, 300),  # follows input audio length
        "resolutions": ("720p",),
        "aspect_ratios": (),  # follows the portrait image
        "audio_always_on": True,  # audio is the required driving input, not optional
        "rate_usd_per_second": {"720p": 0.0505},
        "source_url": "https://kie.ai/kling-ai-avatar",
        "requires_image_and_audio_input": True,
    },
    "kling/ai-avatar-pro": {
        "display_name": "Kling AI Avatar 2.0 — pro (1080p, 48fps)",
        "duration_seconds_range": (1, 300),
        "resolutions": ("1080p",),
        "aspect_ratios": (),
        "audio_always_on": True,
        "rate_usd_per_second": {"1080p": 0.101},
        "source_url": "https://kie.ai/kling-ai-avatar",
        "requires_image_and_audio_input": True,
    },
}

CATALOG_VERIFIED_AT = "2026-11-16T00:00:00Z"
API_BASE_URL = "https://api.kie.ai"
CREATE_TASK_PATH = "/api/v1/jobs/createTask"
POLL_TASK_PATH = "/api/v1/jobs/recordInfo"


def plan_total_duration_seconds(plan: UGCPlan) -> int:
    return sum(scene.duration_seconds for scene in plan.scenes)


def _rate_for(model_entry: dict[str, Any], resolution: str, audio: bool) -> float:
    rates = model_entry["rate_usd_per_second"]
    per_resolution = rates.get(resolution)
    if per_resolution is None:
        raise KieError(f"resolution {resolution!r} is not priced for this model")
    if isinstance(per_resolution, dict):
        key = "audio" if audio else "no_audio"
        return per_resolution[key]
    return per_resolution


def _catalog_entry(model: str) -> dict[str, Any]:
    entry = KIE_CATALOG.get(model)
    if entry is None:
        raise KieError(f"model {model!r} is not in the verified Kie catalog (known: {sorted(KIE_CATALOG)})")
    return entry


def estimate_scene_cost_usd(
    model: str, duration_seconds: int, *, resolution: str | None, audio: bool | None
) -> dict[str, Any]:
    """Cost for ONE scene == one Kie job, since `execute_plan` submits one
    `createTask` per scene (see its loop). A model's duration range is a
    per-generation limit, not a whole-plan budget — validate per scene."""
    entry = _catalog_entry(model)
    min_d, max_d = entry["duration_seconds_range"]
    if not (min_d <= duration_seconds <= max_d):
        raise KieError(
            f"{model}: scene duration {duration_seconds}s is outside the "
            f"supported per-generation range {min_d}-{max_d}s"
        )
    chosen_resolution = resolution or entry["resolutions"][0]
    if chosen_resolution not in entry["resolutions"]:
        raise KieError(f"{model}: resolution {chosen_resolution!r} not in {entry['resolutions']}")
    chosen_audio = entry["audio_always_on"] if audio is None else bool(audio)
    rate = _rate_for(entry, chosen_resolution, chosen_audio)
    return {
        "duration_seconds": duration_seconds,
        "resolution": chosen_resolution,
        "audio": chosen_audio,
        "rate_usd_per_second": rate,
        "estimated_cost_usd": round(rate * duration_seconds, 4),
    }


def estimate_cost_usd(plan: UGCPlan) -> dict[str, Any]:
    """Pure, no-network cost estimate for the whole plan (one line per scene,
    since each scene is its own Kie job). Never calls Kie; always safe to run.

    Reads `resolution` / `audio` out of `plan.creative_matrix` (a free-form
    dict on UGCPlan) since those aren't first-class UGCPlan fields — the plan
    schema is shared with Higgsfield and isn't being extended for one provider.
    Missing values fall back to the model's cheapest resolution and, for
    audio-optional models, no audio — a caller that wants a specific tier
    must set `plan.creative_matrix["resolution"]` / `["audio"]` explicitly.
    """
    entry = _catalog_entry(plan.model)
    resolution = plan.creative_matrix.get("resolution")
    audio = plan.creative_matrix.get("audio")
    scenes = [
        {"scene_index": scene.index, **estimate_scene_cost_usd(plan.model, scene.duration_seconds, resolution=resolution, audio=audio)}
        for scene in plan.scenes
    ]
    total_cost = round(sum(scene["estimated_cost_usd"] for scene in scenes), 4)
    return {
        "model": plan.model,
        "display_name": entry["display_name"],
        "scene_count": len(scenes),
        "duration_seconds": plan_total_duration_seconds(plan),
        "resolution": scenes[0]["resolution"] if scenes else resolution or entry["resolutions"][0],
        "audio": scenes[0]["audio"] if scenes else bool(entry["audio_always_on"]),
        "scenes": scenes,
        "estimated_cost_usd": total_cost,
        "catalog_source_url": entry["source_url"],
        "catalog_verified_at": CATALOG_VERIFIED_AT,
    }


class KieClient:
    """Fail-closed adapter for Kie.ai, compatible with the Higgsfield provider
    contract (`doctor`, `preflight`, `execute_plan`). Does not replace, wrap,
    or modify HiggsfieldClient — Higgsfield stays exactly as it is.

    Two independent kill switches, both default false (mirrors the layered
    pattern already established for Kie elsewhere in the LUZYA ecosystem,
    e.g. factory-ia-channel-v5's NO-SPEND invariants):
      - KIE_ENABLED: the adapter will talk to Kie at all (doctor/preflight).
      - KIE_LIVE_EXECUTION: `execute_plan` may actually submit a paid job.
        Flipping this is an explicit, manual owner decision — nothing in
        this codebase sets it automatically.
    Without KIE_LIVE_EXECUTION, `execute_plan` always raises before any
    network call: it returns plan-only cost/validation info via `preflight`
    and `estimate_cost_usd` instead of ever touching the live API.
    """

    def __init__(
        self,
        *,
        enabled: bool | None = None,
        live_execution: bool | None = None,
        api_key: str | None = None,
        max_retries: int = 3,
    ) -> None:
        self.enabled = enabled if enabled is not None else os.getenv("KIE_ENABLED", "false").lower() == "true"
        self.live_execution = (
            live_execution
            if live_execution is not None
            else os.getenv("KIE_LIVE_EXECUTION", "false").lower() == "true"
        )
        self._api_key = api_key if api_key is not None else os.getenv("KIE_API_KEY")
        self.max_retries = max_retries

    def doctor(self) -> dict[str, Any]:
        has_key = bool(self._api_key)
        if not self.enabled:
            status = "DISABLED"
        elif not has_key:
            status = "API_KEY_MISSING"
        elif not self.live_execution:
            status = "PLAN_ONLY"
        else:
            status = "LIVE_EXECUTION_ARMED"
        return {
            "enabled": self.enabled,
            "api_key_present": has_key,
            "live_execution": self.live_execution,
            "catalog_models": sorted(KIE_CATALOG),
            "catalog_verified_at": CATALOG_VERIFIED_AT,
            "status": status,
        }

    def preflight(self, plan: UGCPlan) -> dict[str, Any]:
        """Pure validation — never makes a network call. Confirms the plan is
        shaped correctly for Kie and returns the real cost estimate, but
        cannot and does not confirm live API key validity (that requires a
        real request, gated by KIE_LIVE_EXECUTION, which this method never
        performs)."""
        if not self.enabled:
            raise KieError("Kie is disabled; set KIE_ENABLED=true to allow even plan-only checks")
        estimate = estimate_cost_usd(plan)
        return {
            "model_known": True,
            "live_execution": self.live_execution,
            "api_key_present": bool(self._api_key),
            **estimate,
        }

    def execute_plan(
        self,
        plan: UGCPlan,
        approval: Approval,
        output_dir: Path,
        *,
        budget_usd: float,
    ) -> list[Path]:
        if not self.enabled:
            raise KieError("Kie is disabled; set KIE_ENABLED=true")
        if approval.scope_id != plan.scope_id:
            raise KieError("approval scope does not match immutable plan scope")

        estimate = estimate_cost_usd(plan)  # raises on unknown model / bad duration / resolution
        if estimate["estimated_cost_usd"] > budget_usd:
            raise KieBudgetExceededError(
                f"estimated cost ${estimate['estimated_cost_usd']:.4f} exceeds the "
                f"authorized budget ${budget_usd:.4f} for {plan.model}"
            )

        if not self.live_execution:
            raise KieError(
                "Kie live execution is disabled (KIE_LIVE_EXECUTION=false). "
                "The plan passed validation and budget check "
                f"(estimated ${estimate['estimated_cost_usd']:.4f}), but no job "
                "has been submitted and no credit has been spent. Set "
                "KIE_LIVE_EXECUTION=true only after explicit owner approval "
                "for this specific generation."
            )
        if not self._api_key:
            raise KieError("KIE_API_KEY is not set; cannot make a live request")

        output_dir.mkdir(parents=True, exist_ok=True)
        results: list[Path] = []
        for scene in plan.scenes:
            target = output_dir / f"scene-{scene.index}.mp4"
            evidence = output_dir / f"scene-{scene.index}.json"
            if target.exists() and evidence.exists():
                results.append(target)
                continue
            task_id = self._create_task(plan, scene)
            payload = self._poll_until_done(task_id)
            url = self._extract_result_url(payload)
            self._download(url, target)
            evidence.write_text(
                json.dumps(
                    {
                        "task_id": task_id,
                        "response": payload,
                        "scope_id": plan.scope_id,
                        "estimated_cost_usd": estimate["estimated_cost_usd"],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            results.append(target)
            time.sleep(5)
        return results

    def _create_task(self, plan: UGCPlan, scene: Scene) -> str:
        entry = KIE_CATALOG[plan.model]
        resolution = plan.creative_matrix.get("resolution") or entry["resolutions"][0]
        audio = plan.creative_matrix.get("audio", entry["audio_always_on"])
        body = {
            "model": plan.model,
            "input": {
                "prompt": scene.spoken_text,
                "duration": scene.duration_seconds,
                "resolution": resolution,
                "aspect_ratio": "9:16" if "9:16" in entry.get("aspect_ratios", ()) else None,
                "audio": bool(audio),
            },
            "callBackUrl": None,
        }
        payload = self._request_json_with_retry("POST", CREATE_TASK_PATH, body)
        task_id = payload.get("data", {}).get("taskId") or payload.get("taskId")
        if not task_id:
            raise KieError(f"Kie createTask response had no taskId: {payload}")
        return str(task_id)

    def _poll_until_done(self, task_id: str, *, timeout_seconds: int = 1800, interval_seconds: int = 10) -> Any:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            payload = self._request_json_with_retry("GET", f"{POLL_TASK_PATH}?taskId={task_id}", None)
            state = (payload.get("data") or {}).get("state") or payload.get("state")
            if state in ("success", "completed", "SUCCESS"):
                return payload
            if state in ("fail", "failed", "FAILED"):
                raise KieError(f"Kie task {task_id} failed: {payload}")
            time.sleep(interval_seconds)
        raise KieError(f"Kie task {task_id} timed out after {timeout_seconds}s")

    def _request_json_with_retry(self, method: Literal["GET", "POST"], path: str, body: dict | None) -> Any:
        last_error = "unknown error"
        for attempt in range(1, self.max_retries + 1):
            try:
                return self._request_json(method, path, body)
            except KieError as error:
                last_error = str(error)
                if self._non_retryable(last_error):
                    break
                if attempt < self.max_retries:
                    time.sleep(attempt * 10)
        raise KieError(f"Kie request failed: {last_error[:500]}")

    def _request_json(self, method: Literal["GET", "POST"], path: str, body: dict | None) -> Any:
        url = f"{API_BASE_URL}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as error:  # narrowed to KieError for the retry loop above
            raise KieError(str(error)) from error

    @staticmethod
    def _non_retryable(message: str) -> bool:
        text = message.lower()
        markers = ("unauthorized", "invalid api key", "401", "not found", "invalid param", "insufficient credit")
        return any(marker in text for marker in markers)

    @staticmethod
    def _extract_result_url(payload: Any) -> str:
        data = payload.get("data") if isinstance(payload, dict) else None
        for container in (data, payload):
            if not isinstance(container, dict):
                continue
            for key in ("resultUrl", "result_url", "url"):
                if container.get(key):
                    return str(container[key])
            results = container.get("resultUrls") or container.get("results")
            if isinstance(results, list) and results:
                return str(results[0])
        raise KieError(f"result URL not found in Kie response: {payload}")

    @staticmethod
    def _download(url: str, target: Path) -> None:
        from urllib.request import urlretrieve

        urlretrieve(url, target)
