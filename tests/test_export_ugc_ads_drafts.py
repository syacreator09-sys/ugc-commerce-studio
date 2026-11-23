import importlib.util
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("ugc_exports", ROOT/"scripts"/"export_ugc_ads_drafts.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def test_three_drafts_and_controlled_hooks(tmp_path):
    records=mod.build(tmp_path)
    assert len(records)==3
    for record in records:
        folder=tmp_path/record["campaign"]
        script=json.loads((folder/"script.json").read_text())
        ads=json.loads((folder/"meta-ads-draft.json").read_text())
        assert len(script["scenes"])==6 and script["duration_seconds"]==30
        assert all(scene["end"]-scene["start"]==5 for scene in script["scenes"])
        assert len(ads["variants"])==3
        assert len({tuple(v["body_scene_ids"]) for v in ads["variants"]})==1
        assert all(v["status"]=="NOT_RENDERED" and not v["publish"] for v in ads["variants"])
        assert not (folder/"master.mp4").exists()
        assert not (folder/"thumbnail.png").exists()

def test_reject_unapproved_six_scene_mismatch():
    import copy
    source=json.loads(mod.CAMPAIGNS.read_text())
    campaign=copy.deepcopy(source["campaigns"][0])
    campaign["scenes"].pop()
    with pytest.raises(ValueError,match="6 contiguous"):
        mod.assert_preset(campaign)

def test_reject_approved_budget_on_draft_export():
    import copy
    source=json.loads(mod.CAMPAIGNS.read_text())
    campaign=copy.deepcopy(source["campaigns"][0])
    campaign["scope"]["premium_generation_approved"]=True
    with pytest.raises(ValueError,match="budgeted"):
        mod.assert_preset(campaign)

def test_evidence_is_not_fake(tmp_path):
    mod.build(tmp_path)
    for record in json.loads(mod.CAMPAIGNS.read_text())["campaigns"]:
        folder=tmp_path/record["id"]
        brief=json.loads((folder/"creative-brief.json").read_text())
        qa=json.loads((folder/"qa-checklist.json").read_text())
        assert brief["facts_verified"]==[]
        assert qa["release_gate"]=="BLOCKED_NO_MASTER"
