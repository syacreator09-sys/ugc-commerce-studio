import pytest

from ugc_commerce.domain import Approval, ProductManifest, Scene, UGCPlan, UGCProfile
from ugc_commerce.kie import KieBudgetExceededError, KieClient, KieError, estimate_cost_usd, estimate_scene_cost_usd
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
        media_assets=["front.jpg"],
        commercial_rights_status="approved",
    )


def kie_plan(*, model="minimax-h3/text-to-video", scene_durations=(10,), resolution=None, audio=None):
    plan = build_plan(product(), UGCProfile(brand_name="Cano", cta="Compra"), workflow="direct_scene", model=model)
    base = plan.scenes[0]
    plan.scenes = [
        Scene(
            index=i + 1,
            goal=base.goal,
            natural_text=base.natural_text,
            spoken_text=base.spoken_text,
            caption_text=base.caption_text,
            vibe=base.vibe,
            visual_direction=base.visual_direction,
            duration_seconds=duration,
        )
        for i, duration in enumerate(scene_durations)
    ]
    if resolution is not None:
        plan.creative_matrix["resolution"] = resolution
    if audio is not None:
        plan.creative_matrix["audio"] = audio
    return plan


# --- estimate_cost_usd: pure, no network, must match Kie.ai's own verified pricing ---

def test_minimax_h3_768p_rate_matches_kie_own_page():
    plan = kie_plan(model="minimax-h3/text-to-video", scene_durations=(10,), resolution="768p")
    estimate = estimate_cost_usd(plan)
    assert estimate["scenes"][0]["rate_usd_per_second"] == 0.04
    assert estimate["estimated_cost_usd"] == pytest.approx(0.40)


def test_minimax_h3_2k_rate_matches_kie_own_page():
    plan = kie_plan(model="minimax-h3/text-to-video", scene_durations=(10,), resolution="2k")
    estimate = estimate_cost_usd(plan)
    assert estimate["scenes"][0]["rate_usd_per_second"] == 0.065
    assert estimate["estimated_cost_usd"] == pytest.approx(0.65)


def test_kling_o3_720p_audio_toggle_changes_price():
    no_audio = estimate_cost_usd(kie_plan(model="kling-3.0-omni/text-to-video", scene_durations=(8,), resolution="720p", audio=False))
    with_audio = estimate_cost_usd(kie_plan(model="kling-3.0-omni/text-to-video", scene_durations=(8,), resolution="720p", audio=True))
    assert no_audio["scenes"][0]["rate_usd_per_second"] == 0.0755
    assert with_audio["scenes"][0]["rate_usd_per_second"] == 0.101
    assert with_audio["estimated_cost_usd"] > no_audio["estimated_cost_usd"]


def test_kling_ai_avatar_standard_rate():
    plan = kie_plan(model="kling/ai-avatar-standard", scene_durations=(15,), resolution="720p")
    estimate = estimate_cost_usd(plan)
    assert estimate["scenes"][0]["rate_usd_per_second"] == 0.0505
    assert estimate["estimated_cost_usd"] == pytest.approx(0.0505 * 15)


def test_multi_scene_plan_prices_each_scene_as_its_own_generation():
    # execute_plan submits one createTask per scene, so a 5x5s plan must be
    # valid for a 15s-per-generation-cap model (each scene fits individually),
    # and total cost must be the sum of each scene's own cost — not a single
    # job priced against the summed duration.
    plan = kie_plan(model="minimax-h3/text-to-video", scene_durations=(5, 5, 5, 5, 5), resolution="768p")
    estimate = estimate_cost_usd(plan)
    assert estimate["scene_count"] == 5
    assert estimate["duration_seconds"] == 25
    assert len(estimate["scenes"]) == 5
    assert all(scene["estimated_cost_usd"] == pytest.approx(0.20) for scene in estimate["scenes"])
    assert estimate["estimated_cost_usd"] == pytest.approx(1.00)


def test_unknown_model_is_rejected():
    plan = kie_plan(model="not-a-real-model")
    with pytest.raises(KieError, match="not in the verified Kie catalog"):
        estimate_cost_usd(plan)


def test_duration_outside_model_range_is_rejected():
    # Scene itself caps duration_seconds at [4, 15], a range every Kie model
    # here happens to accept — so this is tested directly against the
    # per-scene validator (a plain int, not a Scene) rather than via a plan,
    # to actually exercise a value each model's own range rejects.
    with pytest.raises(KieError, match="outside the supported per-generation range"):
        estimate_scene_cost_usd("minimax-h3/text-to-video", 20, resolution="768p", audio=None)  # max is 15
    with pytest.raises(KieError, match="outside the supported per-generation range"):
        estimate_scene_cost_usd("kling-3.0-omni/text-to-video", 2, resolution="720p", audio=False)  # min is 3


# --- fail-closed invariants: the two kill switches must both default false ---

def test_disabled_by_default_blocks_even_plan_only_preflight():
    client = KieClient()  # no env overrides; must read real env defaults as false
    assert client.enabled is False
    assert client.live_execution is False
    with pytest.raises(KieError, match="disabled"):
        client.preflight(kie_plan())


def test_preflight_succeeds_when_enabled_without_touching_network():
    client = KieClient(enabled=True, live_execution=False, api_key="fake-key-never-used")
    status = client.preflight(kie_plan(scene_durations=(10,), resolution="768p"))
    assert status["model_known"] is True
    assert status["live_execution"] is False
    assert status["estimated_cost_usd"] == pytest.approx(0.40)


def test_execute_plan_never_submits_when_live_execution_is_false(monkeypatch, tmp_path):
    client = KieClient(enabled=True, live_execution=False, api_key="fake-key-never-used")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("execute_plan must never reach the network when KIE_LIVE_EXECUTION is false")

    monkeypatch.setattr(client, "_create_task", fail_if_called)
    monkeypatch.setattr(client, "_request_json", fail_if_called)

    plan = kie_plan(scene_durations=(10,), resolution="768p")
    approval = Approval(scope_id=plan.scope_id, approved_by="owner")
    with pytest.raises(KieError, match="live execution is disabled"):
        client.execute_plan(plan, approval, tmp_path, budget_usd=5.0)


def test_execute_plan_rejects_mismatched_approval_scope_before_any_network_call(monkeypatch, tmp_path):
    client = KieClient(enabled=True, live_execution=True, api_key="fake-key-never-used")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("must reject before making any network call")

    monkeypatch.setattr(client, "_create_task", fail_if_called)

    plan = kie_plan()
    approval = Approval(scope_id="scope_wrong", approved_by="owner")
    with pytest.raises(KieError, match="approval scope"):
        client.execute_plan(plan, approval, tmp_path, budget_usd=5.0)


def test_execute_plan_enforces_budget_cap_before_any_network_call(monkeypatch, tmp_path):
    client = KieClient(enabled=True, live_execution=True, api_key="fake-key-never-used")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("must reject before making any network call")

    monkeypatch.setattr(client, "_create_task", fail_if_called)

    plan = kie_plan(model="kling-3.0-omni/text-to-video", scene_durations=(15,), resolution="4k")  # expensive
    approval = Approval(scope_id=plan.scope_id, approved_by="owner")
    with pytest.raises(KieBudgetExceededError, match="exceeds the authorized budget"):
        client.execute_plan(plan, approval, tmp_path, budget_usd=5.0)


def test_execute_plan_requires_api_key_even_when_fully_armed(tmp_path):
    client = KieClient(enabled=True, live_execution=True, api_key=None)
    plan = kie_plan(scene_durations=(10,), resolution="768p")
    approval = Approval(scope_id=plan.scope_id, approved_by="owner")
    with pytest.raises(KieError, match="KIE_API_KEY"):
        client.execute_plan(plan, approval, tmp_path, budget_usd=5.0)


def test_doctor_reports_plan_only_without_making_a_network_call():
    client = KieClient(enabled=True, live_execution=False, api_key="fake-key-never-used")
    status = client.doctor()
    assert status["status"] == "PLAN_ONLY"
    assert status["enabled"] is True
    assert status["live_execution"] is False


def test_doctor_reports_disabled_by_default():
    client = KieClient(enabled=False)
    assert client.doctor()["status"] == "DISABLED"
