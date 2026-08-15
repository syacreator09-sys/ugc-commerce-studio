import json
import subprocess

import pytest

from ugc_commerce.domain import Approval, ProductManifest, UGCProfile
from ugc_commerce.higgsfield import HiggsfieldClient, HiggsfieldError
from ugc_commerce.planner import build_plan


def product():
    return ProductManifest(
        product_id="p",
        ownership_type="affiliate",
        platform="tiktok_shop",
        title="Producto",
        source_url="https://example.com/p",
        affiliate_url="https://example.com/a",
        availability="available",
        price_amount=1,
        verified_benefits=["beneficio"],
        media_assets=["front.jpg", "side.jpg", "detail.jpg"],
        commercial_rights_status="approved",
    )


def completed(command, returncode=0, stdout="{}", stderr=""):
    return subprocess.CompletedProcess(command, returncode, stdout, stderr)


def test_direct_scene_uses_start_image_and_explicit_wait_timeout():
    plan = build_plan(product(), UGCProfile(brand_name="Cano", cta="Compra"), workflow="direct_scene")
    command = HiggsfieldClient(enabled=True)._command_for_scene(plan, plan.scenes[0], product_id=None)
    assert "--start-image" in command
    assert "kling3_0" in command
    assert command[command.index("--wait-timeout") + 1] == "20m"


def test_marketing_studio_passes_product_avatar_audio_and_30m_wait_timeout():
    profile = UGCProfile(brand_name="Cano", cta="Compra", avatar_id="avatar-1", avatar_type="custom")
    plan = build_plan(product(), profile)
    command = HiggsfieldClient(enabled=True)._command_for_scene(plan, plan.scenes[0], product_id="product-1")
    assert "marketing_studio_video" in command
    assert "--product_ids" in command
    assert "--avatars" in command
    assert "--generate_audio" in command
    assert command[command.index("--wait-timeout") + 1] == "30m"

    product_file = command[command.index("--product_ids") + 1][1:]
    avatar_file = command[command.index("--avatars") + 1][1:]
    with open(product_file, encoding="utf-8") as handle:
        assert json.load(handle) == ["product-1"]
    with open(avatar_file, encoding="utf-8") as handle:
        assert json.load(handle) == [{"id": "avatar-1", "type": "custom"}]


def test_preflight_checks_cli_auth_and_live_model_before_generation(monkeypatch):
    plan = build_plan(product(), UGCProfile(brand_name="Cano", cta="Compra"))
    client = HiggsfieldClient(enabled=True)
    calls = []

    def fake_run(command, *, allow_disabled=False):
        calls.append(command)
        return completed(command, stdout='{"ok": true}')

    monkeypatch.setattr(client, "_run", fake_run)
    status = client.preflight(plan)

    assert status["cli_installed"] is True
    assert status["authenticated"] is True
    assert status["model_available"] is True
    assert ["higgsfield", "version"] in calls
    assert ["higgsfield", "account", "status", "--json"] in calls
    assert ["higgsfield", "model", "get", "marketing_studio_video", "--json"] in calls


def test_preflight_fails_fast_when_cli_is_missing(monkeypatch):
    plan = build_plan(product(), UGCProfile(brand_name="Cano", cta="Compra"))
    client = HiggsfieldClient(enabled=True)

    def fake_run(command, *, allow_disabled=False):
        if command[1:] == ["version"]:
            return completed(command, returncode=127, stdout="", stderr="higgsfield CLI not found")
        raise AssertionError("preflight must stop after missing CLI")

    monkeypatch.setattr(client, "_run", fake_run)
    with pytest.raises(HiggsfieldError, match="CLI"):
        client.preflight(plan)


def test_preflight_fails_fast_when_auth_expired(monkeypatch):
    plan = build_plan(product(), UGCProfile(brand_name="Cano", cta="Compra"))
    client = HiggsfieldClient(enabled=True)

    def fake_run(command, *, allow_disabled=False):
        if command[1:] == ["version"]:
            return completed(command)
        if command[1:3] == ["account", "status"]:
            return completed(command, returncode=1, stdout="", stderr="Session expired")
        raise AssertionError("preflight must stop before model lookup when auth fails")

    monkeypatch.setattr(client, "_run", fake_run)
    with pytest.raises(HiggsfieldError, match="auth login"):
        client.preflight(plan)


def test_execute_plan_runs_preflight_before_product_or_generation(monkeypatch, tmp_path):
    plan = build_plan(product(), UGCProfile(brand_name="Cano", cta="Compra"))
    approval = Approval(scope_id=plan.scope_id, approved_by="tester")
    client = HiggsfieldClient(enabled=True)
    order = []

    def fake_preflight(received_plan):
        assert received_plan.scope_id == plan.scope_id
        order.append("preflight")
        raise HiggsfieldError("preflight stop")

    monkeypatch.setattr(client, "preflight", fake_preflight)
    monkeypatch.setattr(client, "_ensure_product", lambda _: order.append("product"))

    with pytest.raises(HiggsfieldError, match="preflight stop"):
        client.execute_plan(plan, approval, tmp_path)
    assert order == ["preflight"]


def test_scope_mismatch_is_blocked_before_cli_preflight(monkeypatch, tmp_path):
    plan = build_plan(product(), UGCProfile(brand_name="Cano", cta="Compra"))
    approval = Approval(scope_id="wrong", approved_by="tester")
    client = HiggsfieldClient(enabled=True)
    monkeypatch.setattr(client, "preflight", lambda _: (_ for _ in ()).throw(AssertionError("must not call CLI")))

    with pytest.raises(HiggsfieldError, match="scope"):
        client.execute_plan(plan, approval, tmp_path)
