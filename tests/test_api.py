import pytest

pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from recommender.api import app  # noqa: E402

client = TestClient(app)

EXAMPLE = {"age": 9, "diagnosis_context": "pediatric_oncology", "treatment_phase": "active_high_fatigue",
           "known_sensitivities": ["photosensitive_seizure_trigger"], "preferred_genres": ["Comedy", "Animation"]}


def test_post_returns_top5_with_breakdown_rules_and_an_exclusion():
    r = client.post("/recommendations", json=EXAMPLE)
    assert r.status_code == 200
    body = r.json()
    assert len(body["recommendations"]) == 5
    first = body["recommendations"][0]
    assert {"taste_score", "taste_breakdown", "penalty_total", "final_score", "rules_evaluated", "explanation"} <= set(first)
    assert len(body["excluded_candidates"]) >= 1
    assert body["audit"]["hard_rule_violations_in_results"] == 0


def test_unknown_sensitivity_is_rejected_not_silently_ignored():
    bad = dict(EXAMPLE, known_sensitivities=["photosensitive_seizure_triger"])  # typo
    assert client.post("/recommendations", json=bad).status_code == 422


def test_no_patient_id_lookup_needed():
    assert client.post("/recommendations", json={"age": 40, "diagnosis_context": "other", "treatment_phase": "stable"}).status_code == 200
