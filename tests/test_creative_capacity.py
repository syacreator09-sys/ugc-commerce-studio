from ugc_commerce.creative_capacity import CreativeCapacityInput, assess_creative_capacity


def test_low_capacity_recommends_one_or_zero_not_mass_generation():
    report = assess_creative_capacity(CreativeCapacityInput(hooks=["one"] ))
    assert report.score < 35
    assert report.recommended_initial_creatives in {0, 1}


def test_diverse_product_recommends_five_initial_tests_before_signal():
    report = assess_creative_capacity(CreativeCapacityInput(
        hooks=["h1","h2","h3","h4"],
        audiences=["a1","a2"],
        use_cases=["u1","u2","u3"],
        demonstrations=["d1","d2"],
        objections=["o1","o2"],
        transformations=["t1"],
        formats=["review","pov","tutorial","problem-solution","comparison"],
    ))
    assert report.score >= 80
    assert report.recommended_initial_creatives == 5


def test_only_proven_winner_can_recommend_ten_plus():
    report = assess_creative_capacity(CreativeCapacityInput(
        hooks=["h1","h2","h3","h4"], audiences=["a1","a2"], use_cases=["u1","u2","u3"],
        demonstrations=["d1","d2","d3"], objections=["o1","o2"], transformations=["t1","t2"],
        formats=["review","pov","tutorial","problem-solution","comparison"], proven_winner=True,
    ))
    assert report.recommended_initial_creatives == "10+"


def test_duplicates_do_not_inflate_creative_capacity():
    report = assess_creative_capacity(CreativeCapacityInput(hooks=["same","same","same"], formats=["pov","pov"]))
    assert report.unique_counts["hooks"] == 1
    assert report.unique_counts["formats"] == 1
