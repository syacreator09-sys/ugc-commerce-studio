import json
from pathlib import Path

from jsonschema import Draft202012Validator, validate

from ugc_commerce.creative_capacity import CreativeCapacityInput
from ugc_commerce.economics import EconomicsScenario, calculate_affiliate_economics
from ugc_commerce.offers import EvidenceValue, ProductOfferSnapshot
from ugc_commerce.product_intelligence import analyze_product_offer
from ugc_commerce.product_scout_score import ChannelFitTier, ProductScoutInput


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"


def schema(name: str) -> dict:
    return json.loads((CONTRACTS / name).read_text(encoding="utf-8"))


def strong_offer() -> ProductOfferSnapshot:
    return ProductOfferSnapshot(
        platform="tiktok_shop",
        market="MX",
        seller_name="Demo seller",
        product_id="schema-demo",
        title="Pantalla LED flexible",
        price_amount=EvidenceValue.verified(899, source="product page"),
        currency=EvidenceValue.verified("MXN", source="product page"),
        organic_commission_amount=EvidenceValue.verified(181.9, source="affiliate detail"),
        shop_ads_commission_rate=EvidenceValue.verified(0.01, source="affiliate detail"),
        free_sample_available=EvidenceValue.verified(True, source="invitation"),
        stock_status=EvidenceValue.verified("in_stock", source="product page"),
        sales_count=EvidenceValue.verified(2500, source="product page"),
        review_count=EvidenceValue.verified(450, source="product page"),
        rating=EvidenceValue.verified(4.7, source="product page"),
        commercial_rights_status="approved",
        source_provenance=["product page", "affiliate detail", "invitation"],
    )


def scout() -> ProductScoutInput:
    return ProductScoutInput(
        commission_mxn=181.9,
        understandable_in_3s=True,
        has_clear_visual_change=True,
        is_photogenic=True,
        channel_fit=ChannelFitTier.PERFECT,
        solves_specific_common_pain=True,
        is_impulse_priced=False,
        is_trending=True,
        has_good_url_images=True,
        no_real_action_video_required=False,
        simple_avatar_and_script=True,
    )


def creative() -> CreativeCapacityInput:
    return CreativeCapacityInput(
        hooks=["transformación", "curiosidad", "negocio", "setup"],
        audiences=["negocios", "creadores"],
        use_cases=["señalización", "setup", "eventos"],
        demonstrations=["encendido", "mensaje", "flexibilidad"],
        objections=["tamaño", "configuración"],
        transformations=["apagado a encendido"],
        formats=["demo", "pov", "review", "tutorial"],
    )


def test_public_contract_schemas_are_valid_draft_2020_12():
    for filename in (
        "product-offer-snapshot.schema.json",
        "affiliate-economics.schema.json",
        "product-intelligence-report.schema.json",
    ):
        Draft202012Validator.check_schema(schema(filename))


def test_offer_serialization_validates_against_public_contract():
    validate(instance=strong_offer().model_dump(mode="json"), schema=schema("product-offer-snapshot.schema.json"))


def test_economics_serialization_validates_against_public_contract():
    economics = calculate_affiliate_economics(
        strong_offer(),
        scenarios=[EconomicsScenario(name="base", views=1000, ctr=0.02, cvr=0.05)],
    )
    validate(instance=economics.model_dump(mode="json"), schema=schema("affiliate-economics.schema.json"))


def test_product_intelligence_serialization_validates_against_public_contract():
    report = analyze_product_offer(
        strong_offer(),
        scout(),
        creative(),
        scenarios=[EconomicsScenario(name="base", views=1000, ctr=0.02, cvr=0.05)],
    )
    validate(instance=report.model_dump(mode="json"), schema=schema("product-intelligence-report.schema.json"))
