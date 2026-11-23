#!/usr/bin/env python3
"""Export commercial-ready DRAFT documents from canonical demo campaigns.

No video generation, image generation, advertising API, credits or publication.
Never creates fake video/thumbnail/real metrics.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGNS = ROOT / "commercial_portfolio" / "campaigns.json"
BEATS = ("hook", "problem", "product", "demonstration", "benefit", "cta")
HEADLINES = {
 "demo-a-ecommerce": ["Tu escritorio, otra historia", "Una idea para ordenar", "Conoce el concepto MODULA"],
 "demo-b-beauty": ["Una estética más cuidada", "Descubre el concepto NUBA", "Belleza en los detalles"],
 "demo-c-performance": ["¿Qué cambiarías aquí?", "Un rincón, dos ambientes", "La diferencia está en la luz"],
}
ENGLISH = {
 "demo-a-ecommerce": "Conceptual 30-second product UGC ad for a fictional desk-organizer brand. Six-scene storyboard, three hook options, Spanish voice script, and production-safe captions. Video production and licensing remain pending; no performance claims.",
 "demo-b-beauty": "Premium beauty/lifestyle commercial concept for a fictional mist. Editorial product photography direction, restrained Spanish UGC narration, six scene beats, and compliance-aware creative. No product outcomes, testimonial or completed video are claimed.",
 "demo-c-performance": "Controlled-hook performance creative concept for a fictional reading lamp. Three alternative intros, fixed shared body and CTA, six-scene storyboard and a proposed experiment matrix. No actual lift or winning variation is claimed.",
}
SPANISH = {
 "demo-a-ecommerce": "Concepto UGC para organizador ficticio MODULA. Seis escenas, guion en español y tres hooks; master y derechos comerciales pendientes.",
 "demo-b-beauty": "Concepto de anuncio beauty premium para NUBA, producto ficticio. Dirección de arte, seis escenas y copy sin promesas cosméticas. Sin video final.",
 "demo-c-performance": "Anuncio conceptual de performance para LUMO: tres hooks controlados, cuerpo común y CTA idéntico. Resultados de campañas inexistentes; no atribuir métricas.",
}
OFFERS = {
 "AI UGC Video Ads": "1 vertical master, 6 scenes, 1 hook, hard cuts, licensed avatar/product, captions, 1 revision round (script before render). Extra paid regenerations quoted after estimate.",
 "AI Product Commercials": "1 product-focused vertical master, up to 6 scenes, product macro inserts, 1 art-direction board, captions, 1 revision round, source rights required.",
 "Performance Creative Variations": "1 shared body and CTA, 3 controlled hook alternatives, 3 review masters, a hypothesis sheet and UTM naming; no guaranteed performance.",
}

def assert_preset(campaign):
    if campaign.get("production_preset") != "santmun_parity_30s":
        raise ValueError("Unexpected production preset")
    scenes = campaign["scenes"]
    if len(scenes) != 6 or [(s["start"], s["end"]) for s in scenes] != [(i*5,(i+1)*5) for i in range(6)]:
        raise ValueError("Expected 6 contiguous five-second scenes")
    if len(campaign["hooks"]) != 3 or not all(campaign["hooks"]):
        raise ValueError("Three hook options required")
    if campaign["rights"]["status"] != "PENDING_SOURCE_APPROVAL" or not campaign["product"]["fictional"]:
        raise ValueError("This tool exports only unapproved fictional demos")
    if campaign["scope"]["premium_generation_approved"] or campaign["scope"]["max_spend_usd"] is not None:
        raise ValueError("Do not export approved or budgeted jobs with this draft-only tool")


def produce(campaign, dest):
    assert_preset(campaign)
    name = campaign["id"]
    dest.mkdir(parents=True,exist_ok=True)
    script = {
      "schema_version":"1.0", "campaign_id":name, "preset":"santmun_parity_30s",
      "status":"PREPRODUCTION_ONLY", "language":"es-LATAM", "fps":30,
      "width":1080, "height":1920, "duration_seconds":30,
      "scenes":[
        {"scene_id":f"{name}-s{i+1:02}", "beat":BEATS[i],"start":s["start"],"end":s["end"],
         "natural_text":s["voice"],"spoken_text":s["voice"],"caption_text":s["voice"],
         "visual_direction":s["visual"],"overlay":s["overlay"],"avatar_id":None,"voice_review":"PENDING"}
        for i,s in enumerate(campaign["scenes"])
      ],
      "hooks":[{"variant":chr(65+i),"text":h,"controlled_variable":"hook"} for i,h in enumerate(campaign["hooks"])],
      "rights_status":"PENDING", "source_kind":"FICTIONAL_DEMO",
      "master_mp4":None, "premium_approval":False, "publish_approved":False
    }
    filebase=f"CANO_UGC_{name.upper().replace('-','_')}_ES_9x16_30S"
    variants=[]
    for i,h in enumerate(campaign["hooks"]):
        label="ABC"[i]
        variants.append({
         "name":f"{filebase}_HOOK_{label}_V01",
         "status":"NOT_RENDERED", "placement":"IG_Reels_FB_Reels_Stories",
         "hook":h,"body_scene_ids":[s["scene_id"] for s in script["scenes"][1:]],
         "headline":HEADLINES[name][i],"primary_text":campaign["copy"],
         "cta":campaign["cta"], "conversion_destination":"PENDING_USER_APPROVAL",
         "hypothesis":f"H{label}: {h} may change three-second hold vs other hooks",
         "metrics":["impressions","3_second_video_plays","video_thruplays","link_clicks","landing_page_views","purchases"],
         "reporting":{"measured":False,"winner":None,"sample_size":None},
         "ai_content_check_required":True, "commercial_rights_check_required":True,
         "publish":False
        })
    portfolio={
      "campaign_id":name,"fictional_demo":True,"delivered_assets":["script.json","storyboard.json","meta-ads-draft.json",
      "creative-brief.json","qa-checklist.json","upwork-case.md"],
      "pending_assets":["master.mp4","scene-01.mp4 ... scene-06.mp4","thumbnail.png","subtitles.srt",
      "captions.json","production-manifest.json","qa-report.json","cost-report.json"],
      "english_description":ENGLISH[name],"spanish_description":SPANISH[name],
      "tools_used_verified":["Python (preproduction export)"],"tools_planned_not_executed":["Higgsfield","FFmpeg","Whisper or HyperFrames"],
      "cost_actual_usd":0, "cost_video_estimate_usd":None,
      "source_rights_verified":False, "qa_verified":False,"master_verified":False
    }
    brief={"brand":campaign["brand"],"product":campaign["product"],"product_fictional":True,
           "audience":"Mexico Spanish-speaking demo viewers", "format":"UGC 9:16", "intent":campaign["type"],
           "claim_status":"UNVERIFIED_FICTIONAL", "facts_verified":[],"facts_unknown":campaign["claims"]["facts_unknown"],
           "claims_forbidden":campaign["claims"]["claims_forbidden"],"rights":campaign["rights"],
           "source":"commercial_portfolio/campaigns.json", "creative_intelligence_evidence":"hypothesis",
           "hook_types":["question","demonstration","curiosity"],
           "script_structure":"ugc_discovery","proof_type":"none"}
    checklist={"technical":{"dimensions_1080x1920":"NOT_TESTED","fps_30":"NOT_TESTED","codec_h264_aac":"NOT_TESTED",
                 "audio_normalized":"NOT_TESTED","captions_burned":"NOT_TESTED","duration_30s":"NOT_TESTED"},
               "human":{"avatar_rights":"PENDING","lip_sync":"PENDING","pronunciation":"PENDING",
                        "product_identity":"PENDING","commercial_claims":"PENDING","captions_safe_zone":"PENDING",
                        "hook_first_3s":"PENDING","cta_visible":"PENDING"},
               "release_gate":"BLOCKED_NO_MASTER"}
    files={
      "script.json":script, "storyboard.json":{"campaign":name,"scenes":script["scenes"],"status":"DRAFT"},
      "meta-ads-draft.json":{"status":"NOT_PUBLISHED","variants":variants,"recommended_test":"Compare single-variable hook; retain identical body/CTA/landing and audience across variants","ad_spend":0},
      "creative-brief.json":brief, "qa-checklist.json":checklist
    }
    for filename,value in files.items():
        (dest/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    case=f"""# {name} — Fictional commercial demo (NOT A FINISHED VIDEO)

## English
{ENGLISH[name]}

## Español
{SPANISH[name]}

## Hook candidates
""" + "\n".join(f"- {label}: {v['hook']}" for label,v in zip("ABC",variants)) + f"""

## Production and rights
- Audio/video master: NOT RENDERED.
- Product is fictional and all claims are conceptual.
- Talent/avatar, music, product media and final publication require rights verification.
- Estimated paid provider spend: NOT QUOTED. Actual paid spend: USD 0.
- QA, performance and ad results: NOT VERIFIED.
"""
    (dest/"upwork-case.md").write_text(case,encoding="utf-8")
    return files


def build(outdir, source=CAMPAIGNS):
    source_data=json.loads(source.read_text(encoding="utf-8"))
    if source_data.get("schema_version")!="1.0":raise ValueError("Unsupported campaign schema")
    records=[]
    for c in source_data["campaigns"]:
        files=produce(c,outdir/c["id"])
        records.append({"campaign":c["id"],"files":list(files)+["upwork-case.md"]})
    (outdir/"service-offers.json").write_text(json.dumps({"status":"DRAFT","offers":OFFERS,
      "pricing":"QUOTE_AFTER_PROVIDER_COST_AND_SCOPE_CONFIRMATION",
      "revision_policy":"1 included script revision; re-generation credits and additional revision fees quoted before approval",
      "claims":"NO_GUARANTEED_RESULTS"},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return records


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,default=CAMPAIGNS)
    ap.add_argument("--output",type=Path,default=ROOT/"commercial_portfolio"/"production_drafts")
    args=ap.parse_args()
    print(json.dumps(build(args.output,args.source),ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
