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


if __name__ == "__main__":
    app()
