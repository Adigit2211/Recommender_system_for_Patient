"""Tests for the safety rules"""
import copy

import pytest

from recommender import engine
from recommender.engine import VetoViolation, load_movies, load_rule_data, recommend
from recommender.rules import load_rules, validate_rule

MOVIES = load_movies()
RULES = load_rule_data()


def profile(**kw):
    base = {"age": 30, "diagnosis_context": "other", "treatment_phase": "stable", "known_sensitivities": [],
            "preferred_genres": [], "preferred_tones": [], "liked_titles": [], "diversity_rerank": True}
    base.update(kw)
    return base


def by_title(title):
    return next(m for m in MOVIES if m["title"] == title)


# --- hand-written checks ---
def test_photosensitive_never_gets_flagged_or_unchecked_flashing():
    for genres in ([], ["Action"], ["Animation", "Comedy"], ["Adventure"], ["Music"]):
        r = recommend(profile(known_sensitivities=["photosensitive_seizure_trigger"], preferred_genres=genres))
        for e in r["recommendations"]:
            assert by_title(e["title"])["sensitivity_tags"]["flashing_strobe_content"] == "none", e["title"]


def test_incredibles2_always_removed_for_photosensitive_even_if_perfect_taste_match():
    p = profile(known_sensitivities=["photosensitive_seizure_trigger"], age=9,
                preferred_genres=["Animation", "Action", "Adventure", "Family"], liked_titles=["The Incredibles"])
    r = recommend(p)
    assert "Incredibles 2" not in [e["title"] for e in r["recommendations"]]
    assert "Incredibles 2" in [e["title"] for e in r["excluded_candidates"]]


def test_minor_never_gets_r_rated():
    r = recommend(profile(age=15, preferred_genres=["Drama", "Crime", "Horror", "War"]))
    assert all(e["mpa_rating"] != "R" for e in r["recommendations"])


def test_grief_sensitive_never_gets_death_theme():
    r = recommend(profile(age=9, known_sensitivities=["grief_sensitive"], preferred_genres=["Animation", "Drama"]))
    for e in r["recommendations"]:
        assert "death_or_loss" not in by_title(e["title"])["sensitivity_tags"]["theme_flags"]


def test_sick_child_never_gets_illness_centred_film():
    r = recommend(profile(age=15, diagnosis_context="pediatric_oncology", preferred_genres=["Drama", "Romance"]))
    for e in r["recommendations"]:
        assert "central_serious_illness" not in by_title(e["title"])["sensitivity_tags"]["theme_flags"]


# --- nothing later in the pipeline can bring a removed movie back ---
def test_huge_taste_score_cannot_resurrect_a_vetoed_title(monkeypatch):
    real = engine.taste

    def rigged(profile, movie, liked):
        out = real(profile, movie, liked)
        if movie["title"] == "Incredibles 2":
            out = {**out, "score": 999.0}
        return out
    monkeypatch.setattr(engine, "taste", rigged)
    r = recommend(profile(known_sensitivities=["photosensitive_seizure_trigger"], age=9, preferred_genres=["Animation"]))
    assert "Incredibles 2" not in [e["title"] for e in r["recommendations"]]


def test_diversity_stage_cannot_resurrect_a_vetoed_title(monkeypatch):
    bad = by_title("Incredibles 2")

    def evil_diversify(ranked, k):
        injected = copy.deepcopy(ranked[0])
        injected.update(title=bad["title"], franchise=bad["franchise"], director=bad["director"])
        return [injected] + ranked[: k - 1], ["injected vetoed title"]
    monkeypatch.setattr(engine, "_diversify", evil_diversify)
    with pytest.raises(VetoViolation):
        recommend(profile(known_sensitivities=["photosensitive_seizure_trigger"], age=9, preferred_genres=["Animation"]))


def test_audit_catches_a_hard_violation_that_slipped_past_stage_one(monkeypatch):
    # pretend step 1 is broken and lets everything through; the final check should still stop it
    monkeypatch.setattr(engine, "evaluate_rules", lambda rules, p, m: [])
    with pytest.raises(VetoViolation):
        recommend(profile(known_sensitivities=["photosensitive_seizure_trigger"], age=9,
                          preferred_genres=["Animation", "Action"], liked_titles=[]))


def test_penalty_scale_never_changes_the_excluded_set():
    p = profile(age=9, diagnosis_context="pediatric_oncology", treatment_phase="active_high_fatigue",
                known_sensitivities=["photosensitive_seizure_trigger"], preferred_genres=["Comedy"])
    sets = [{e["title"] for e in recommend(p, penalty_scale=s)["excluded_candidates"]} for s in (0.0, 0.5, 1.0, 5.0)]
    assert all(s == sets[0] for s in sets)


# --- penalties stay separate from taste ---
def test_final_equals_taste_plus_separate_penalty():
    r = recommend(profile(age=9, diagnosis_context="pediatric_oncology", treatment_phase="active_high_fatigue",
                          preferred_genres=["Animation"]))
    for e in r["recommendations"]:
        assert e["final_score"] == pytest.approx(e["taste_score"] + e["penalty_total"], abs=1e-3)
        assert e["penalty_total"] == pytest.approx(sum(p["penalty"] for p in e["soft_penalties_applied"]), abs=1e-3)
        assert e["penalty_total"] <= 0


def test_fatigue_demotes_long_film_but_does_not_remove_it():
    base = profile(preferred_genres=["Action", "Adventure", "Science Fiction"], age=30)
    fat = dict(base, treatment_phase="active_high_fatigue")
    r0 = recommend(dict(base, diversity_rerank=False), k=66)
    r1 = recommend(dict(fat, diversity_rerank=False), k=66)
    s0 = {e["title"]: e for e in r0["recommendations"]}
    s1 = {e["title"]: e for e in r1["recommendations"]}
    assert "Avengers: Endgame" in s1  # still eligible
    assert s1["Avengers: Endgame"]["penalty_total"] < s0["Avengers: Endgame"]["penalty_total"]


# --- rules with no matching movie in the dataset, tested on made-up movies ---
def synthetic(**over):
    m = copy.deepcopy(by_title("Paddington"))
    m["title"] = "Synthetic"
    for k, v in over.items():
        if k == "mpa_rating":
            m["mpa_rating"] = v
        elif k == "subtitles":
            m["sensitivity_tags"]["accessibility"]["subtitles_available"] = v
    return m


def test_nc17_hard_excluded_for_minor_synthetic():
    r = recommend(profile(age=17), movies=[by_title("Paddington"), synthetic(mpa_rating="NC-17")])
    assert "Synthetic" in [e["title"] for e in r["excluded_candidates"]]


def test_subtitles_false_hard_excluded_synthetic():
    r = recommend(profile(known_sensitivities=["needs_subtitles"]),
                  movies=[by_title("Paddington"), synthetic(subtitles=False)])
    assert "Synthetic" in [e["title"] for e in r["excluded_candidates"]]


# --- the rules file itself ---
def test_unknown_condition_key_fails_loudly():
    rule = copy.deepcopy(RULES["rules"][0])
    rule["content_condition"] = {"flashh_in": ["confirmed_present"]}  # deliberate typo
    with pytest.raises(ValueError):
        validate_rule(rule)


def test_every_rule_is_tagged_and_sourced_or_inferred():
    for r in load_rules()["rules"]:
        assert r["justification_type"] in ("sourced", "inferred_from_source", "inferred")
        assert r["source"].strip()
        assert (r["severity"] == "hard_exclude") == (r["penalty_weight"] is None)


def test_dataset_values_are_in_vocabulary():
    for m in MOVIES:
        t = m["sensitivity_tags"]
        assert t["flashing_strobe_content"] in {"none", "mild", "confirmed_present", "unknown"}
        assert t["thematic_intensity"] in {"low", "medium", "high"}
        assert t["pacing_complexity"] in {"simple", "moderate", "dense"}
        assert 40 <= len(MOVIES) <= 80


def test_diversity_limits_franchise_repeats():
    r = recommend(profile(age=9, preferred_genres=["Animation"]))
    fr = [e["franchise"] for e in r["recommendations"]]
    assert len(fr) == len(set(fr))


def test_weak_matches_are_flagged():
    # a 16-year-old horror fan: R-rated horror is blocked, so most picks can't match
    r = recommend(profile(age=16, diagnosis_context="pediatric_oncology", preferred_genres=["Horror", "Thriller"]))
    weak = [e for e in r["recommendations"] if e["weak_taste_match"]]
    assert weak and any("weak taste" in w for w in r["warnings"])
