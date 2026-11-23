"""Six-scene reviewed creative → existing validated UGCPlan. Never spends credits."""
import hashlib
import json

import pytest

from scripts.build_six_scene_plan import canonical_plan
from scripts.export_ugc_ads_drafts import build as export_drafts
from ugc_commerce.domain import UGCPlan


def fixture(tmp_path, *, production=True):
    export_drafts(tmp_path / "drafts")
    source = tmp_path / "drafts" / "demo-a-ecommerce" / "script.json"
    script = json.loads(source.read_text(encoding="utf-8"))
    if production:
        script.update(status="APPROVED_FOR_PRODUCTION", rights_status="APPROVED",
                      source_kind="VERIFIED_PRODUCT", premium_approval=False,
                      publish_approved=False)
        source.write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")
    product = {
        "product_id": "approved-modula",
        "ownership_type": "owned", "platform": "own_store",
        "title": "Organizador MODULA", "availability": "available",
        "price_amount": 100,
        "verified_benefits": ["permite organizar lápices y plumas"],
        "media_assets": ["approved-front.png", "approved-side.png", "approved-back.png"],
        "commercial_rights_status": "approved",
        "prohibited_claims": ["cura", "100% sostenible"],
    }
    profile = {"brand_name": "MODULA", "cta": "Conoce el organizador", "language": "es-LATAM"}
    pf, pp = tmp_path / "product.json", tmp_path / "profile.json"
    pf.write_text(json.dumps(product), encoding="utf-8")
    pp.write_text(json.dumps(profile), encoding="utf-8")
    return source, pf, pp


def make_plan(source, pf, pp, **kwargs):
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    return canonical_plan(source, pf, pp, approved_script_sha256=digest,
                          reviewed_by="human QA", **kwargs)


def test_fictional_draft_never_creates_premium_plan(tmp_path):
    source, pf, pp = fixture(tmp_path, production=False)
    with pytest.raises(ValueError, match="Approved script"):
        make_plan(source, pf, pp)


def test_reviewed_real_product_produces_six_scene_existing_schema(tmp_path):
    source, pf, pp = fixture(tmp_path)
    plan = make_plan(source, pf, pp)
    assert isinstance(plan, UGCPlan)
    assert len(plan.scenes) == 6
    assert [scene.duration_seconds for scene in plan.scenes] == [5] * 6
    assert plan.scope_id.startswith("scope_")
    assert plan.creative_matrix["reviewed_commercial_script"]["reviewed_by"] == "human QA"
    assert plan.auto_publish is False
    assert plan.human_review_required is True
    assert plan.product.commercial_rights_status == "approved"


def test_script_hash_is_immutable(tmp_path):
    source, pf, pp = fixture(tmp_path)
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        canonical_plan(source, pf, pp, approved_script_sha256="0" * 64, reviewed_by="human QA")


def test_rights_hard_gate_blocks_even_with_reviewed_script(tmp_path):
    source, pf, pp = fixture(tmp_path)
    product = json.loads(pf.read_text())
    product["commercial_rights_status"] = "pending"
    pf.write_text(json.dumps(product))
    with pytest.raises(ValueError, match="commercial rights"):
        make_plan(source, pf, pp)


def test_forbidden_claim_blocks(tmp_path):
    source, pf, pp = fixture(tmp_path)
    script = json.loads(source.read_text())
    script["scenes"][0]["spoken_text"] = "Cura todo, MODULA"
    source.write_text(json.dumps(script))
    with pytest.raises(ValueError, match="Prohibited product claim"):
        make_plan(source, pf, pp)


def test_scene_timeline_change_blocks(tmp_path):
    source, pf, pp = fixture(tmp_path)
    script = json.loads(source.read_text())
    script["scenes"][2]["end"] = 18
    source.write_text(json.dumps(script))
    with pytest.raises(ValueError, match="five-second"):
        make_plan(source, pf, pp)
