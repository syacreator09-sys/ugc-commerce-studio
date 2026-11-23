"""Guard against double billing on ambiguous or interrupted provider jobs."""
import json
import subprocess
import pytest

from ugc_commerce.domain import Approval, ProductManifest, UGCProfile
from ugc_commerce.higgsfield import HiggsfieldClient, HiggsfieldError
from ugc_commerce.planner import build_plan


def test_ambiguous_502_never_retries(monkeypatch):
    calls = []
    client = HiggsfieldClient(enabled=True, max_retries=3)
    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 1, "", "HTTP 502 Bad Gateway")
    monkeypatch.setattr(client, "_run", fake_run)
    with pytest.raises(HiggsfieldError, match="AMBIGUOUS_REMOTE_SUBMISSION"):
        client._run_json_with_retry(["higgsfield", "generate", "create", "kling3_0"])
    assert len(calls) == 1


def test_timeout_never_retries(monkeypatch):
    calls = []
    client = HiggsfieldClient(enabled=True, max_retries=3)
    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 124, "", "timed out")
    monkeypatch.setattr(client, "_run", fake_run)
    with pytest.raises(HiggsfieldError, match="AMBIGUOUS_REMOTE_SUBMISSION"):
        client._run_json_with_retry(["higgsfield", "generate", "create", "kling3_0"])
    assert len(calls) == 1


def approved_plan():
    product = ProductManifest(
        product_id="approved-product", ownership_type="owned", platform="own_store",
        title="Real approved desk organizer", availability="available",
        price_amount=100, verified_benefits=["displays stationery on desk"],
        media_assets=["licensed1.png", "licensed2.png", "licensed3.png"],
        commercial_rights_status="approved",
    )
    plan = build_plan(product, UGCProfile(brand_name="Demo", cta="Explore"),
                      workflow="direct_scene")
    return plan


def test_interrupted_scene_receipt_blocks_second_paid_submission(tmp_path, monkeypatch):
    plan = approved_plan()
    approval = Approval(scope_id=plan.scope_id, approved_by="operator")
    client = HiggsfieldClient(enabled=True)
    monkeypatch.setattr(client, "preflight", lambda _: {"status": "READY"})
    calls = []
    def simulated_ambiguous(*args, **kwargs):
        calls.append(1)
        raise HiggsfieldError("AMBIGUOUS_REMOTE_SUBMISSION: timeout")
    monkeypatch.setattr(client, "_run_json_with_retry", simulated_ambiguous)
    with pytest.raises(HiggsfieldError, match="AMBIGUOUS_REMOTE_SUBMISSION"):
        client.execute_plan(plan, approval, tmp_path)
    receipt = tmp_path / "scene-1.submission.json"
    assert receipt.is_file()
    payload = json.loads(receipt.read_text())
    assert payload["status"] == "SUBMISSION_UNRESOLVED"
    assert payload["scope_id"] == plan.scope_id

    with pytest.raises(HiggsfieldError, match="UNRESOLVED_SCENE_SUBMISSION"):
        client.execute_plan(plan, approval, tmp_path)
    assert len(calls) == 1


def test_partial_download_without_receipt_never_auto_resubmits(tmp_path, monkeypatch):
    plan = approved_plan()
    approval = Approval(scope_id=plan.scope_id, approved_by="operator")
    (tmp_path / "scene-1.mp4").write_bytes(b"partial")
    client = HiggsfieldClient(enabled=True)
    monkeypatch.setattr(client, "preflight", lambda _: {"status": "READY"})
    monkeypatch.setattr(client, "_run_json_with_retry",
                        lambda _: (_ for _ in ()).throw(AssertionError("NO SECOND BILL")))
    with pytest.raises(HiggsfieldError, match="UNRESOLVED_SCENE_SUBMISSION"):
        client.execute_plan(plan, approval, tmp_path)
