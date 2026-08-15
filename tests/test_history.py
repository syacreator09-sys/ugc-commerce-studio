from ugc_commerce.history import append_history, best_baseline, build_baselines, load_history
from ugc_commerce.performance import PublicationPerformance


def test_history_aggregates_real_observations_by_channel():
    records = [
        PublicationPerformance(product_id="p1", creative_id="c1", channel="cano", views=1000, product_clicks=20, orders=2, organic_commission_mxn=160),
        PublicationPerformance(product_id="p2", creative_id="c2", channel="cano", views=500, product_clicks=5, orders=1, organic_commission_mxn=80),
        PublicationPerformance(product_id="p3", creative_id="c3", channel="cass", views=1000, product_clicks=10, orders=0, organic_commission_mxn=0),
    ]
    baselines = build_baselines(records, dimension="channel")
    cano = next(b for b in baselines if b.key == "cano")
    assert cano.observations == 2
    assert cano.views == 1500
    assert cano.orders == 3
    assert cano.total_commission_mxn == 240
    assert round(cano.ctr, 6) == round(25/1500, 6)
    assert cano.commission_per_1000_views == 160


def test_best_baseline_uses_observed_commission_per_1000_views():
    records = [
        PublicationPerformance(product_id="p1", creative_id="c1", format="pov", views=1000, orders=1, organic_commission_mxn=100),
        PublicationPerformance(product_id="p2", creative_id="c2", format="review", views=1000, orders=2, organic_commission_mxn=300),
    ]
    best = best_baseline(build_baselines(records, dimension="format"))
    assert best is not None
    assert best.key == "review"


def test_extended_learning_dimensions_are_supported():
    records = [
        PublicationPerformance(
            product_id="p1", creative_id="c1", seller_name="seller-a", price_band="500-999",
            presenter_id="avatar-cass", ugc_angle="problem-solution", views=1000,
            product_clicks=20, orders=2, organic_commission_mxn=160,
        ),
        PublicationPerformance(
            product_id="p2", creative_id="c2", seller_name="seller-a", price_band="500-999",
            presenter_id="avatar-cass", ugc_angle="review", views=500,
            product_clicks=5, orders=1, organic_commission_mxn=80,
        ),
    ]
    assert build_baselines(records, dimension="seller_name")[0].key == "seller-a"
    assert build_baselines(records, dimension="price_band")[0].key == "500-999"
    assert build_baselines(records, dimension="presenter_id")[0].key == "avatar-cass"
    assert {b.key for b in build_baselines(records, dimension="ugc_angle")} == {"problem-solution", "review"}


def test_history_jsonl_round_trip_persists_owned_performance_dataset(tmp_path):
    path = tmp_path / "performance.jsonl"
    first = PublicationPerformance(product_id="p1", creative_id="c1", channel="cano", views=1000, product_clicks=20, orders=2, organic_commission_mxn=160)
    second = PublicationPerformance(product_id="p1", creative_id="c2", channel="cano", views=800, product_clicks=12, orders=1, shop_ads_commission_mxn=40)

    append_history(path, first)
    append_history(path, second)
    loaded = load_history(path)

    assert [r.creative_id for r in loaded] == ["c1", "c2"]
    assert loaded[0].organic_commission_mxn == 160
    assert loaded[1].shop_ads_commission_mxn == 40


def test_missing_history_file_returns_empty_dataset(tmp_path):
    assert load_history(tmp_path / "missing.jsonl") == []


def test_empty_history_has_no_fabricated_baseline():
    assert build_baselines([], dimension="channel") == []
    assert best_baseline([]) is None
