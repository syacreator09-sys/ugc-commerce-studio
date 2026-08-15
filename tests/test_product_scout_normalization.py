from ugc_commerce.product_scout_score import ChannelFitTier, ProductScoutInput, score_product


def test_legacy_total_remains_90_while_normalized_score_is_100():
    result = score_product(ProductScoutInput(
        commission_mxn=160,
        understandable_in_3s=True,
        has_clear_visual_change=True,
        is_photogenic=True,
        channel_fit=ChannelFitTier.PERFECT,
        solves_specific_common_pain=True,
        is_impulse_priced=True,
        is_trending=True,
        has_good_url_images=True,
        no_real_action_video_required=True,
        simple_avatar_and_script=True,
    ))
    assert result.total == 90
    assert result.raw_score == 90
    assert result.normalized_score == 100.0


def test_normalized_score_clamps_negative_risk_only_total_to_zero():
    result = score_product(ProductScoutInput(
        commission_mxn=0,
        understandable_in_3s=False,
        has_clear_visual_change=False,
        is_photogenic=False,
        channel_fit=ChannelFitTier.NONE,
        solves_specific_common_pain=False,
        is_impulse_priced=False,
        is_trending=False,
        requires_medical_claims=True,
    ))
    assert result.total == -10
    assert result.raw_score == 0
    assert result.normalized_score == 0.0


def test_unknown_commission_scores_zero_without_inventing_value():
    result = score_product(ProductScoutInput(
        commission_mxn=None,
        understandable_in_3s=True,
        has_clear_visual_change=True,
        is_photogenic=True,
        channel_fit=ChannelFitTier.GOOD,
        solves_specific_common_pain=True,
        is_impulse_priced=False,
        is_trending=False,
    ))
    assert result.commission_points == 0
