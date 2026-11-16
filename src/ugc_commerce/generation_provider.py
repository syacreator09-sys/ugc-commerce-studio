from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Protocol

from .domain import Approval, UGCPlan


class GenerationProvider(Protocol):
    """Structural contract every video-generation provider must satisfy.

    Higgsfield (`higgsfield.HiggsfieldClient`) already matches this shape by
    construction. A new provider only needs to implement these three methods
    with the same signatures — nothing here replaces or wraps Higgsfield.
    """

    def doctor(self) -> dict[str, Any]: ...

    def preflight(self, plan: UGCPlan) -> dict[str, Any]: ...

    def execute_plan(self, plan: UGCPlan, approval: Approval, output_dir: Path) -> list[Path]: ...


def get_provider(name: str | None = None) -> GenerationProvider:
    """Resolve a provider by name, defaulting to the existing env-driven choice.

    Defaults to "higgsfield" when nothing is specified, so existing callers
    (CLI, scripts) keep their current behavior unless they opt into Kie.
    """
    selected = (name or os.getenv("UGC_PROVIDER", "higgsfield")).strip().lower()
    if selected == "higgsfield":
        from .higgsfield import HiggsfieldClient

        return HiggsfieldClient()
    if selected == "kie":
        from .kie import KieClient

        return KieClient()
    raise ValueError(f"Unknown generation provider: {selected!r} (expected 'higgsfield' or 'kie')")
