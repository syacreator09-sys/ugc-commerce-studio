from ugc_commerce.history import best_baseline, build_baselines
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


def test_empty_history_has_no_fabricated_baseline():
    assert build_baselines([], dimension="channel") == []
    assert best_baseline([]) is None
