from ugc_commerce.performance import PublicationPerformance, calculate_performance


def test_performance_metrics_use_correct_names_and_math():
    result = calculate_performance(PublicationPerformance(
        product_id="p", creative_id="c", views=1000, product_clicks=20, orders=2,
        organic_commission_mxn=160, shop_ads_commission_mxn=20, gmv_mxn=1000,
    ))
    assert result.ctr == 0.02
    assert result.cvr == 0.10
    assert result.total_commission_mxn == 180
    assert result.commission_per_view == 0.18
    assert result.commission_per_1000_views == 180
    assert result.commission_per_order == 90
    assert not hasattr(result, "cpv")


def test_zero_denominators_are_safe():
    result = calculate_performance(PublicationPerformance(product_id="p", creative_id="c", views=0, product_clicks=0, orders=0))
    assert result.ctr == 0
    assert result.cvr == 0
    assert result.commission_per_view == 0
    assert result.commission_per_1000_views == 0
    assert result.commission_per_order == 0
