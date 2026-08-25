import json
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, validate

from ugc_commerce.priors import CommercePerformancePriorV1
from ugc_commerce.review_evidence import CommerceReviewEvidenceV1


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"


def _schema(name: str) -> dict:
    return json.loads((CONTRACTS / name).read_text(encoding="utf-8"))


def test_mio_bridge_contract_schemas_are_valid_and_match_models():
    prior_schema = _schema("commerce-performance-prior-v1.schema.json")
    review_schema = _schema("commerce-review-evidence-v1.schema.json")
    Draft202012Validator.check_schema(prior_schema)
    Draft202012Validator.check_schema(review_schema)

    prior = CommercePerformancePriorV1(
        prior_id="mio-prior-0123456789abcdef0123",
        platform="tiktok",
        window_hours=72,
        filters={"hook_family": "problem-solution"},
        sample_size=8,
        ctr_median=0.02,
        cvr_median=0.05,
        ctr_stdev=0.005,
        cvr_stdev=0.01,
        classification="PROMISING",
        confidence_score=67,
        source_refs=["mio:metrics-72h"],
        causal_claim=False,
        generated_at=datetime.now(timezone.utc),
    )
    validate(instance=prior.model_dump(mode="json"), schema=prior_schema)

    review = CommerceReviewEvidenceV1(
        evidence_id="review-digest:0123456789abcdef0123",
        product_ref="led-1",
        sample_size=12,
        average_rating=4.2,
        recurring_complaints=["confusing setup"],
        source_refs=["reviews:1"],
        provenance=["product-ip-factory:ReviewDigest"],
        generated_at=datetime.now(timezone.utc),
    )
    validate(instance=review.model_dump(mode="json"), schema=review_schema)
