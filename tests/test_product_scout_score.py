from ugc_commerce.product_scout_score import (
    ChannelFitTier,
    ProductScoutInput,
    ScoutDecision,
    score_product,
)


def strong_input(**overrides) -> ProductScoutInput:
    """A product that should clear PROCEDE on every axis."""
    base = {
        "commission_mxn": 160,
        "understandable_in_3s": True,
        "has_clear_visual_change": True,
        "is_photogenic": True,
        "channel_fit": ChannelFitTier.PERFECT,
        "solves_specific_common_pain": True,
        "is_impulse_priced": True,
        "is_trending": True,
        "has_good_url_images": True,
        "no_real_action_video_required": True,
        "simple_avatar_and_script": True,
    }
    base.update(overrides)
    return ProductScoutInput(**base)


def weak_input(**overrides) -> ProductScoutInput:
    """A product that should score at the floor of every axis."""
    base = {
        "commission_mxn": 5,
        "understandable_in_3s": False,
        "has_clear_visual_change": False,
        "is_photogenic": False,
        "channel_fit": ChannelFitTier.NONE,
        "solves_specific_common_pain": False,
        "is_impulse_priced": False,
        "is_trending": False,
        "has_good_url_images": False,
        "no_real_action_video_required": False,
        "simple_avatar_and_script": False,
    }
    base.update(overrides)
    return ProductScoutInput(**base)


def test_best_case_scores_90_and_procede():
    # 25 (commission) + 20 (visual) + 20 (fit) + 15 (viral) + 0 (risk) + 10 (ease)
    # = 90, the documented per-axis maximum (not 100 -- see module docstring).
    result = score_product(strong_input())
    assert result.commission_points == 25
    assert result.visual_points == 20
    assert result.channel_fit_points == 20
    assert result.viral_points == 15
    assert result.risk_points == 0
    assert result.production_ease_points == 10
    assert result.total == 90
    assert result.decision == ScoutDecision.PROCEDE


def test_worst_case_scores_zero_and_rechazado():
    result = score_product(weak_input())
    assert result.total == 0
    assert result.decision == ScoutDecision.RECHAZADO


def test_commission_tiers():
    assert score_product(weak_input(commission_mxn=150)).commission_points == 25
    assert score_product(weak_input(commission_mxn=149.99)).commission_points == 20
    assert score_product(weak_input(commission_mxn=80)).commission_points == 20
    assert score_product(weak_input(commission_mxn=79.99)).commission_points == 15
    assert score_product(weak_input(commission_mxn=40)).commission_points == 15
    assert score_product(weak_input(commission_mxn=39.99)).commission_points == 5
    assert score_product(weak_input(commission_mxn=20)).commission_points == 5
    assert score_product(weak_input(commission_mxn=19.99)).commission_points == 0


def test_channel_fit_tiers():
    for tier, expected in (
        (ChannelFitTier.PERFECT, 20),
        (ChannelFitTier.GOOD, 12),
        (ChannelFitTier.SO_SO, 5),
        (ChannelFitTier.NONE, 0),
    ):
        assert score_product(weak_input(channel_fit=tier)).channel_fit_points == expected


def test_decision_boundary_60_is_procede():
    inp = weak_input(
        commission_mxn=150,  # 25
        channel_fit=ChannelFitTier.GOOD,  # 12
        solves_specific_common_pain=True,  # 5
        is_impulse_priced=True,  # 5
        has_good_url_images=True,  # 5
        no_real_action_video_required=True,  # 3
        simple_avatar_and_script=True,  # 2 -> 25+12+5+5+5+3+2 = 57 (below 60)
    )
    result = score_product(inp)
    assert result.total == 57
    assert result.decision == ScoutDecision.EN_ESPERA

    inp_at_60 = weak_input(
        commission_mxn=150,  # 25
        channel_fit=ChannelFitTier.GOOD,  # 12
        solves_specific_common_pain=True,  # 5
        is_impulse_priced=True,  # 5
        is_trending=True,  # 5
        has_good_url_images=True,  # 5
        no_real_action_video_required=True,  # 3
        simple_avatar_and_script=True,  # 2 -> total 62
    )
    result_at_60 = score_product(inp_at_60)
    assert result_at_60.total == 62
    assert result_at_60.decision == ScoutDecision.PROCEDE


def test_en_espera_band_55_to_59():
    inp = weak_input(
        commission_mxn=150,  # 25
        channel_fit=ChannelFitTier.SO_SO,  # 5
        understandable_in_3s=True,  # 10
        has_clear_visual_change=True,  # 5
        is_photogenic=True,  # 5
        solves_specific_common_pain=True,  # 5
    )
    # 25 + 5 + 10 + 5 + 5 + 5 = 55
    result = score_product(inp)
    assert result.total == 55
    assert result.decision == ScoutDecision.EN_ESPERA
    assert any("55-59" in reason for reason in result.reasons)


def test_rechazado_below_55():
    inp = weak_input(commission_mxn=150, channel_fit=ChannelFitTier.SO_SO)
    # 25 + 5 = 30
    result = score_product(inp)
    assert result.total == 30
    assert result.decision == ScoutDecision.RECHAZADO


def test_risk_penalty_worst_tier_only_not_additive():
    inp = strong_input(
        requires_medical_claims=False,
        requires_physical_demo_without_vto=True,
        has_known_platform_restrictions=True,
    )
    result = score_product(inp)
    # Both flags set, but only the -5 tier applies once (not -10 for both).
    assert result.risk_points == -5
    assert result.total == 90 - 5


def test_medical_claims_hard_override_rechazado_even_with_perfect_score():
    inp = strong_input(requires_medical_claims=True)
    result = score_product(inp)
    # Numeric total still reflects the -10 penalty, but the decision is
    # forced to RECHAZADO regardless of what the total would otherwise be.
    assert result.total == 90 - 10
    assert result.decision == ScoutDecision.RECHAZADO
    assert any("override" in reason for reason in result.reasons)


def test_production_ease_subchecks_are_independent():
    inp = weak_input(has_good_url_images=True)
    assert score_product(inp).production_ease_points == 5
    inp2 = weak_input(no_real_action_video_required=True)
    assert score_product(inp2).production_ease_points == 3
    inp3 = weak_input(simple_avatar_and_script=True)
    assert score_product(inp3).production_ease_points == 2
