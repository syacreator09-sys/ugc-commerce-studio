import json
from datetime import datetime, timezone

from typer.testing import CliRunner

from ugc_commerce.cli import app


runner = CliRunner()


def _product():
    return {
        "offer": {
            "platform": "tiktok_shop", "market": "MX", "product_id": "p1", "title": "LED",
            "price_amount": {"value": 899, "status": "VERIFIED"},
            "currency": {"value": "MXN", "status": "VERIFIED"},
            "organic_commission_amount": {"value": 181.9, "status": "VERIFIED"},
            "free_sample_available": {"value": True, "status": "VERIFIED"},
            "stock_status": {"value": "in_stock", "status": "VERIFIED"},
            "sales_count": {"value": 1000, "status": "VERIFIED"},
            "review_count": {"value": 100, "status": "VERIFIED"},
            "commercial_rights_status": "approved",
            "source_provenance": ["test"],
        },
        "scout": {
            "commission_mxn": 181.9, "understandable_in_3s": True,
            "has_clear_visual_change": True, "is_photogenic": True,
            "channel_fit": "perfect", "solves_specific_common_pain": True,
            "is_impulse_priced": True, "is_trending": True,
            "has_good_url_images": True, "no_real_action_video_required": True,
            "simple_avatar_and_script": True,
        },
        "creative_capacity": {"hooks": ["h1", "h2", "h3"], "formats": ["pov", "review", "demo"]},
    }


def _prior():
    return {
        "schema_version": "1.0",
        "prior_id": "mio-prior-0123456789abcdef0123",
        "platform": "tiktok",
        "window_hours": 72,
        "filters": {"hook_family": "problem-solution"},
        "sample_size": 8,
        "ctr_median": 0.02,
        "cvr_median": 0.05,
        "ctr_stdev": 0.005,
        "cvr_stdev": 0.01,
        "classification": "PROMISING",
        "confidence_score": 67,
        "source_refs": ["mio:metrics-72h"],
        "causal_claim": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def test_review_signals_cli_returns_angles_not_claims(tmp_path):
    evidence = {
        "schema_version": "1.0",
        "evidence_id": "review-digest:led-1",
        "product_ref": "p1",
        "sample_size": 10,
        "average_rating": 4.3,
        "positive_themes": ["bright"],
        "negative_themes": ["confusing setup"],
        "recurring_complaints": ["confusing setup"],
        "unmet_needs": ["clearer guide"],
        "quality_expectations": ["bright display"],
        "source_refs": ["reviews:1"],
        "provenance": ["product-ip-factory:ReviewDigest"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    path = tmp_path / "review.json"
    path.write_text(json.dumps(evidence), encoding="utf-8")
    result = runner.invoke(app, ["review-signals", "--input", str(path)])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "complaint:confusing setup" in data["angle_candidates"]
    assert "unmet_need:clearer guide" in data["angle_candidates"]
    assert "verified_claims" not in data


def test_factory_order_cli_ingests_mio_brief_and_historical_prior(tmp_path):
    product = tmp_path / "product.json"
    product.write_text(json.dumps(_product()), encoding="utf-8")
    economics = tmp_path / "economics.json"
    economics.write_text(json.dumps({
        "costs": {"currency": "MXN", "generation_cost_mxn": 200},
        "historical_prior": _prior(),
    }), encoding="utf-8")
    brief = tmp_path / "brief.json"
    brief.write_text(json.dumps({
        "schema_version": "1.1",
        "brief_id": "brief-p1",
        "content_type": "ugc-commerce",
        "channel": "cano-digital",
        "narrative_id": "narrative-1",
        "series_id": "series-1",
        "goal": "affiliate conversion",
        "duration": 20,
        "aspect_ratio": "9:16",
        "story_beats": ["hook", "proof", "cta"],
        "experiment_id": "exp-1",
        "variant_id": "var-a",
        "hook_family": "problem-solution",
        "evidence_refs": ["mio:brief-p1"],
        "continuity_refs": [],
        "constraints": [],
    }), encoding="utf-8")
    output = tmp_path / "order.json"

    result = runner.invoke(app, [
        "factory-order",
        "--product", str(product),
        "--economics", str(economics),
        "--channel", "cano",
        "--angle", "problem_solution",
        "--creative-count", "1",
        "--creative-trace", str(brief),
        "--output", str(output),
    ])
    assert result.exit_code == 0, result.output
    summary = json.loads(result.output)
    order = json.loads(output.read_text(encoding="utf-8"))
    assert summary["historical_prior_applied"] is True
    assert summary["mio_brief_id"] == "brief-p1"
    assert order["experiment_id"] == "exp-1"
    assert order["variant_id"] == "var-a"
    assert order["hook_family"] == "problem-solution"
    assert order["economics"]["historical_prior_id"] == "mio-prior-0123456789abcdef0123"
