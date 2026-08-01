#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


def ask(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default


def main() -> int:
    output = Path("config/user-config.json")
    if output.exists():
        raise SystemExit("config/user-config.json already exists; remove it intentionally to rerun setup")

    config = {
        "schema_version": "1.0",
        "brand": {
            "name": ask("Marca", "Cano Digital"),
            "business_type": ask("Tipo: owned, affiliate o both", "both"),
            "audience": ask("Audiencia principal", "México"),
            "default_cta": ask("CTA", "Revisa el precio actual en el enlace del producto"),
        },
        "language": ask("Idioma", "es-LATAM"),
        "tone": ask("Tono", "natural, conversational, trustworthy"),
        "default_mode": ask("Modo UGC", "ugc"),
        "default_workflow": ask("Workflow: marketing_studio o direct_scene", "marketing_studio"),
        "video_model": ask("Modelo direct_scene", "kling3_0"),
        "scene_duration_seconds": int(ask("Duración por escena", "5")),
        "aspect_ratio": "9:16",
        "avatar": {
            "type": ask("Avatar: preset o custom", "preset"),
            "id": ask("Avatar ID, vacío si aún no existe", ""),
            "description": ask("Descripción del presentador", "presentador UGC autorizado"),
        },
        "higgsfield": {
            "enabled": False,
            "generate_audio": True,
            "sequential": True,
            "max_retries": 3,
            "retry_backoff_seconds": [30, 60, 90],
        },
        "policies": {
            "auto_publish": False,
            "auto_activate_ads": False,
            "auto_scale_budget": False,
            "human_review_required": True,
            "premium_generation_requires_approval": True,
            "publication_mode": "draft_only",
        },
        "extra_corrections": {"spoken": {}, "captions": {}},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created {output}. Higgsfield remains disabled until authenticated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
