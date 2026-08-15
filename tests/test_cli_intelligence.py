import json
from typer.testing import CliRunner
from ugc_commerce.cli import app

runner = CliRunner()


def composite_payload():
    return {
        "offer": {
            "platform":"tiktok_shop","market":"MX","product_id":"p1","title":"LED",
            "price_amount":{"value":899,"status":"VERIFIED"},"currency":{"value":"MXN","status":"VERIFIED"},
            "organic_commission_amount":{"value":181.9,"status":"VERIFIED"},
            "free_sample_available":{"value":True,"status":"VERIFIED"},
            "stock_status":{"value":"in_stock","status":"VERIFIED"},
            "sales_count":{"value":1000,"status":"VERIFIED"},"review_count":{"value":100,"status":"VERIFIED"},
            "commercial_rights_status":"approved","source_provenance":["test"]
        },
        "scout": {
            "commission_mxn":181.9,"understandable_in_3s":True,"has_clear_visual_change":True,"is_photogenic":True,
            "channel_fit":"perfect","solves_specific_common_pain":True,"is_impulse_priced":True,"is_trending":True,
            "has_good_url_images":True,"no_real_action_video_required":True,"simple_avatar_and_script":True
        },
        "creative_capacity": {"hooks":["h1","h2","h3"],"formats":["pov","review","demo"]}
    }


def performance_payload(creative_id="c1", *, channel="cano", format="review", commission=160):
    return {
        "product_id":"p1","creative_id":creative_id,"channel":channel,"format":format,
        "views":1000,"product_clicks":20,"orders":2,"organic_commission_mxn":commission,
    }


def test_scout_command_outputs_product_intelligence(tmp_path):
    p=tmp_path/"product.json"; p.write_text(json.dumps(composite_payload()),encoding="utf-8")
    result=runner.invoke(app,["scout","--product",str(p)])
    assert result.exit_code == 0, result.output
    data=json.loads(result.output)
    assert data["product_id"] == "p1"
    assert data["production_decision"] == "PROCEDE"


def test_economics_command_uses_explicit_scenario(tmp_path):
    p=tmp_path/"product.json"; p.write_text(json.dumps(composite_payload()),encoding="utf-8")
    result=runner.invoke(app,["economics","--product",str(p),"--views","1000","--ctr","0.02","--cvr","0.05"])
    assert result.exit_code == 0, result.output
    data=json.loads(result.output)
    assert data["scenarios"][0]["orders"] == 1


def test_discover_tiktok_invitation_preserves_unknown_currency(tmp_path):
    p=tmp_path/"invite.json"; p.write_text(json.dumps({"seller_name":"Shop","title":"LED","displayed_earnings_amount":181.9,"shop_ads_commission_rate":0.01,"free_sample_available":True}),encoding="utf-8")
    result=runner.invoke(app,["discover","--source","tiktok_invitation","--input",str(p)])
    assert result.exit_code == 0, result.output
    data=json.loads(result.output)
    assert data[0]["displayed_earnings_currency"]["status"] == "UNKNOWN"


def test_performance_command_calculates_real_metrics(tmp_path):
    p=tmp_path/"performance.json"; p.write_text(json.dumps(performance_payload()),encoding="utf-8")
    result=runner.invoke(app,["performance","--input",str(p)])
    assert result.exit_code == 0, result.output
    data=json.loads(result.output)
    assert data["ctr"] == 0.02
    assert data["cvr"] == 0.1
    assert data["commission_per_1000_views"] == 160


def test_history_add_and_baselines_commands_persist_and_analyze(tmp_path):
    history=tmp_path/"performance.jsonl"
    first=tmp_path/"first.json"; first.write_text(json.dumps(performance_payload("c1", commission=160)),encoding="utf-8")
    second=tmp_path/"second.json"; second.write_text(json.dumps(performance_payload("c2", commission=80)),encoding="utf-8")

    r1=runner.invoke(app,["history-add","--input",str(first),"--history",str(history)])
    r2=runner.invoke(app,["history-add","--input",str(second),"--history",str(history)])
    assert r1.exit_code == 0, r1.output
    assert r2.exit_code == 0, r2.output

    result=runner.invoke(app,["baselines","--history",str(history),"--dimension","channel"])
    assert result.exit_code == 0, result.output
    data=json.loads(result.output)
    assert data["records"] == 2
    assert data["baselines"][0]["key"] == "cano"
    assert data["baselines"][0]["total_commission_mxn"] == 240
