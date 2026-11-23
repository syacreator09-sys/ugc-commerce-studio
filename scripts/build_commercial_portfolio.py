#!/usr/bin/env python3
"""Generate reproducible, draft-only commercial UGC preproduction packs.

Stdlib-only. Never invokes premium services, generates video or publishes.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "commercial_portfolio" / "campaigns.json"
OUTPUT = ROOT / "commercial_portfolio" / "generated"
ALLOWED_TYPES = {"ecommerce", "beauty", "performance"}


def srt_timestamp(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, rem = divmod(millis, 3600000)
    minutes, rem = divmod(rem, 60000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def validate_campaign(campaign: dict) -> None:
    mandatory = {"id", "type", "brand", "product", "rights", "claims",
                 "scenes", "hooks", "cta", "copy", "upwork"}
    if mandatory - campaign.keys():
        raise ValueError(f"Missing fields for {campaign.get('id')}: {sorted(mandatory-campaign.keys())}")
    if campaign["type"] not in ALLOWED_TYPES:
        raise ValueError("Unknown campaign type")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", campaign["id"]):
        raise ValueError("Unsafe campaign id")
    if not campaign["product"].get("fictional", False):
        raise ValueError("Only explicitly fictional placeholder products supported")
    if campaign["rights"]["status"] != "PENDING_SOURCE_APPROVAL":
        raise ValueError("Only preproduction with pending source rights is allowed")
    if campaign["claims"]["facts_verified"]:
        raise ValueError("Fictional campaigns cannot claim verified commercial facts")
    if len(campaign["hooks"]) < 3:
        raise ValueError("Need at least three hooks")
    if not campaign["scenes"]:
        raise ValueError("Missing scenes")
    end = 0
    for scene in campaign["scenes"]:
        if scene["start"] != end or scene["end"] <= scene["start"]:
            raise ValueError("Scene timeline must be contiguous and positive")
        if not {"visual", "voice", "overlay"} <= scene.keys():
            raise ValueError("Incomplete scene")
        end = scene["end"]
    if end > 60:
        raise ValueError("Campaign exceeds 60 seconds")
    for prohibited in campaign["claims"]["claims_forbidden"]:
        for scene in campaign["scenes"]:
            if prohibited.lower() in scene["voice"].lower():
                raise ValueError("Prohibited claim in voice")


def as_markdown(campaign: dict) -> str:
    lines = [
        f"# {campaign['brand']} — {campaign['id']}",
        "",
        "**STATUS: PREPRODUCCIÓN / SIN VIDEO GENERADO / DEMO SINTÉTICA**",
        "",
        f"Producto: {campaign['product']['name']} (concepto ficticio).",
        "Formato planeado: 9:16, 1080×1920; NO es un archivo master.",
        "",
        "## Guion y storyboard",
        "",
        "| Segundos | Visual planeado | Voz | Texto en pantalla |",
        "|---|---|---|---|",
    ]
    for s in campaign["scenes"]:
        clean = lambda v: str(v).replace("|", "/").replace("\n", " ")
        lines.append(f"| {s['start']}–{s['end']} | {clean(s['visual'])} | {clean(s['voice'])} | {clean(s['overlay'])} |")
    lines += ["", "## Hooks alternativos", ""]
    lines += [f"- {i+1}. {hook}" for i, hook in enumerate(campaign["hooks"])]
    lines += ["", "## Copy de anuncio (borrador)", "", campaign["copy"],
              "", "## Descripción para Upwork", "", campaign["upwork"],
              "", "## QA / bloqueos antes de video",
              "", "- [ ] Sustituir producto ficticio por material propio/autorizado y verificar afirmaciones.",
              "- [ ] Evidencia escrita de derechos de producto, imagen, música, voz y personas.",
              "- [ ] Aprobación explícita del scope_id y presupuesto Higgsfield.",
              "- [ ] Render real, audio, subtítulos sincronizados y master 9:16.",
              "- [ ] Capturas reales y revisión humana de claims/disclosures.",
              "- [ ] Publicación únicamente mediante aprobación posterior.",
              ""]
    return "\n".join(lines)


def build(out_dir: Path, source: Path = INPUT) -> list[Path]:
    data = json.loads(source.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        raise ValueError("Unsupported schema")
    campaigns = data["campaigns"]
    ids = [c["id"] for c in campaigns]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicated campaign IDs")
    for c in campaigns:
        validate_campaign(c)
    outputs = []
    for c in campaigns:
        folder = out_dir / c["id"]
        folder.mkdir(parents=True, exist_ok=True)
        captions = []
        for idx, scene in enumerate(c["scenes"], 1):
            captions.append(f"{idx}\n{srt_timestamp(scene['start'])} --> {srt_timestamp(scene['end'])}\n{scene['voice']}\n")
        manifest = {
            "schema_version": "1.0", "campaign_id": c["id"], "demo_only": True,
            "production_status": "PREPRODUCTION_ONLY",
            "master_video": None, "thumbnail": None,
            "frame": {"aspect_ratio": "9:16", "width": 1080, "height": 1920},
            "planned_duration_seconds": c["scenes"][-1]["end"],
            "hooks": c["hooks"], "rights": c["rights"], "claims": c["claims"],
            "approval": {"scope_id": None, "approved": False},
            "publishing": {"mode": "draft_only", "auto_publish": False, "auto_ads": False},
            "media": {"source_files": [], "licensed_audio": [], "rendered_scenes": []},
            "required_before_delivery": ["source_rights", "product_verification", "render", "human_qa"],
        }
        generated = {
            "README.md": as_markdown(c),
            "captions-draft.srt": "\n".join(captions),
            "manifest.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        }
        for name, content in generated.items():
            target = folder / name
            target.write_text(content, encoding="utf-8")
            outputs.append(target)
    return outputs


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=INPUT)
    p.add_argument("--output", type=Path, default=OUTPUT)
    args = p.parse_args()
    for path in build(args.output, args.input):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
