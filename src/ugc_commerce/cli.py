from __future__ import annotations

import json
from pathlib import Path

import typer

from .distribution import prepare_draft
from .domain import Approval, ProductManifest, UGCPlan, UGCProfile
from .higgsfield import HiggsfieldClient
from .planner import build_plan
from .sources import validate_product

app = typer.Typer(help="Cano UGC Commerce Studio — Higgsfield-only product UGC engine")


def read_model(path: Path, model):
    return model.model_validate_json(path.read_text(encoding="utf-8"))


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _offer_payload(payload: dict):
    return payload.get("offer", payload)


@app.command()
def doctor() -> None:
    """Check local dependencies and Higgsfield connection."""
    status = HiggsfieldClient().doctor()
    typer.echo(json.dumps(status, indent=2))
    if not status["cli_installed"]:
        raise typer.Exit(1)


@app.command("validate-product")
def validate_product_command(product: Path = typer.Option(..., exists=True)) -> None:
    model = read_model(product, ProductManifest)
    warnings = validate_product(model)
    typer.echo(json.dumps({"status": "PASS", "warnings": warnings}, indent=2))


@app.command()
def plan(
    product: Path = typer.Option(..., exists=True),
    profile: Path = typer.Option(..., exists=True),
    output: Path = typer.Option(Path("storage/plan.json")),
    workflow: str = typer.Option("marketing_studio"),
    mode: str = typer.Option("ugc"),
    model: str = typer.Option("kling3_0"),
) -> None:
    product_model = read_model(product, ProductManifest)
    profile_model = read_model(profile, UGCProfile)
    result = build_plan(product_model, profile_model, workflow=workflow, mode=mode, model=model)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    typer.echo(json.dumps({
        "plan": str(output),
        "scope_id": result.scope_id,
        "opportunity": result.opportunity,
        "scenes": len(result.scenes),
        "paid_generation": False,
    }, indent=2))


@app.command()
def approve(
    scope_id: str = typer.Option(...),
    approved_by: str = typer.Option(...),
    output: Path = typer.Option(Path("storage/approval.json")),
) -> None:
    approval = Approval(scope_id=scope_id, approved_by=approved_by)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(approval.model_dump_json(indent=2), encoding="utf-8")
    typer.echo(str(output))


@app.command()
def generate(
    plan_file: Path = typer.Option(..., "--plan", exists=True),
    approval_file: Path = typer.Option(..., "--approval", exists=True),
    output: Path = typer.Option(Path("storage/scenes")),
) -> None:
    plan_model = read_model(plan_file, UGCPlan)
    approval_model = read_model(approval_file, Approval)
    files = HiggsfieldClient().execute_plan(plan_model, approval_model, output)
    typer.echo(json.dumps([str(path) for path in files], indent=2))


@app.command()
def draft(
    plan_file: Path = typer.Option(..., "--plan", exists=True),
    master: Path = typer.Option(..., exists=True),
    output: Path = typer.Option(Path("storage/publication-draft.json")),
) -> None:
    plan_model = read_model(plan_file, UGCPlan)
    publication = prepare_draft(plan_model, master)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(publication.model_dump_json(indent=2), encoding="utf-8")
    typer.echo(str(output))


@app.command()
def scout(product: Path = typer.Option(..., exists=True)) -> None:
    """Analyze one structured affiliate offer without spending generation credits."""
    from .creative_capacity import CreativeCapacityInput
    from .offers import ProductOfferSnapshot
    from .product_intelligence import analyze_product_offer
    from .product_scout_score import ProductScoutInput

    payload = _read_json(product)
    if not isinstance(payload, dict) or "scout" not in payload or "creative_capacity" not in payload:
        raise typer.BadParameter("scout input must contain offer, scout, and creative_capacity objects")
    offer = ProductOfferSnapshot.model_validate(_offer_payload(payload))
    scout_input = ProductScoutInput(**payload["scout"])
    creative = CreativeCapacityInput.model_validate(payload["creative_capacity"])
    report = analyze_product_offer(offer, scout_input, creative)
    typer.echo(report.model_dump_json(indent=2))


@app.command()
def economics(
    product: Path = typer.Option(..., exists=True),
    views: float = typer.Option(1000, min=0),
    ctr: float = typer.Option(..., min=0, max=1),
    cvr: float = typer.Option(..., min=0, max=1),
) -> None:
    """Calculate deterministic affiliate economics for an explicit traffic scenario."""
    from .economics import EconomicsScenario, calculate_affiliate_economics
    from .offers import ProductOfferSnapshot

    payload = _read_json(product)
    if not isinstance(payload, dict):
        raise typer.BadParameter("product input must be a JSON object")
    offer = ProductOfferSnapshot.model_validate(_offer_payload(payload))
    result = calculate_affiliate_economics(
        offer,
        scenarios=[EconomicsScenario(name="cli", views=views, ctr=ctr, cvr=cvr)],
    )
    typer.echo(result.model_dump_json(indent=2))


@app.command()
def discover(
    source: str = typer.Option(..., help="manual or tiktok_invitation"),
    input_file: Path = typer.Option(..., "--input", exists=True),
) -> None:
    """Normalize already-extracted product evidence; discovery never generates media."""
    from .discovery.manual import ManualDiscoveryProvider
    from .providers.tiktok_shop.invitation import normalize_tiktok_invitation

    payload = _read_json(input_file)
    items = payload if isinstance(payload, list) else [payload]
    if not all(isinstance(item, dict) for item in items):
        raise typer.BadParameter("discovery input must be a JSON object or list of objects")
    if source == "manual":
        offers = [candidate.offer for candidate in ManualDiscoveryProvider().discover(items)]
    elif source == "tiktok_invitation":
        offers = [normalize_tiktok_invitation(item, source="tiktok_invitation") for item in items]
    else:
        raise typer.BadParameter("source must be manual or tiktok_invitation")
    typer.echo(json.dumps([offer.model_dump(mode="json") for offer in offers], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
