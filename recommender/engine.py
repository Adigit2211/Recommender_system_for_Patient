"""The recommender itself.

Order matters here:
  1. remove anything a hard rule says this patient must not see
  2. score what's left on taste
  3. subtract soft-rule penalties (kept as their own number, not mixed into taste)
  4. pick the top 5, avoiding repeats from one franchise
  5. re-check the final 5 against every hard rule before returning

Because step 1 happens before everything else, nothing later on can bring a removed movie back.
Step 5 is a safety net in case a bug ever slips through.
"""
import json
from functools import lru_cache
from typing import Any, Dict, List, Tuple

from .explain import explain
from .rules import ROOT, evaluate_rules, hard_violations, load_rules
from .scoring import taste

K = 5
MAX_PER_FRANCHISE = 1
MAX_PER_DIRECTOR = 2
WEAK_TASTE = 0.25  # below this, a movie hardly matches what the patient asked for


class VetoViolation(RuntimeError):
    """Raised if a hard-excluded movie ends up in the results. Should never happen."""


@lru_cache(maxsize=1)
def load_movies() -> List[Dict[str, Any]]:
    return json.loads((ROOT / "data" / "movies.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_rule_data() -> Dict[str, Any]:
    return load_rules()


def _diversify(ranked: List[Dict[str, Any]], k: int) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Walk down the ranked list and skip repeats of the same franchise/director.
    It only chooses from `ranked`, so it can't add a movie that was already removed."""
    chosen, skipped, log = [], [], []
    fr, dr = {}, {}
    for e in ranked:
        if len(chosen) == k:
            break
        if fr.get(e["franchise"], 0) >= MAX_PER_FRANCHISE or dr.get(e["director"], 0) >= MAX_PER_DIRECTOR:
            skipped.append(e)
            log.append(f"skipped '{e['title']}' ({e['franchise']} / {e['director']} already in the list)")
            continue
        chosen.append(e)
        fr[e["franchise"]] = fr.get(e["franchise"], 0) + 1
        dr[e["director"]] = dr.get(e["director"], 0) + 1
    # if there weren't enough different movies, fill up with the ones we skipped
    for e in skipped:
        if len(chosen) == k:
            break
        chosen.append(e)
        log.append(f"added '{e['title']}' back to fill the list")
    return chosen, log


def recommend(profile: Dict[str, Any], movies: List[Dict[str, Any]] = None, rule_data: Dict[str, Any] = None,
              k: int = K, penalty_scale: float = 1.0) -> Dict[str, Any]:
    movies = load_movies() if movies is None else movies
    rule_data = load_rule_data() if rule_data is None else rule_data
    rules = rule_data["rules"]
    warnings: List[str] = []

    by_title = {m["title"].lower(): m for m in movies}
    liked = []
    for t in profile.get("liked_titles", []):
        if t.lower() in by_title:
            liked.append(by_title[t.lower()])
        else:
            warnings.append(f"'{t}' isn't in the movie list, so it was ignored")
    known_genres = {g.lower() for m in movies for g in m["genres"]}
    for g in profile.get("preferred_genres", []):
        if g.lower() not in known_genres:
            warnings.append(f"no movie in the list has the genre '{g}'")

    # don't recommend movies the patient already told us they've seen and liked
    liked_titles = {m["title"] for m in liked}
    candidates = [m for m in movies if m["title"] not in liked_titles]

    # 1. remove anything a hard rule blocks for this patient
    eligible: List[Tuple[Dict[str, Any], List[Dict[str, Any]]]] = []
    excluded: List[Dict[str, Any]] = []
    for m in candidates:
        outcomes = evaluate_rules(rules, profile, m)
        hard = [o for o in outcomes if o["outcome"] == "hard_exclude"]
        if hard:
            excluded.append({"title": m["title"], "hard_rules_fired": [
                {k_: o[k_] for k_ in ("rule_id", "name", "justification_type", "source")} for o in hard]})
        else:
            eligible.append((m, outcomes))
    excluded_titles = {e["title"] for e in excluded}

    # 2 + 3. taste score and penalties, kept separate
    scored = []
    for m, outcomes in eligible:
        t = taste(profile, m, liked)
        soft = [o for o in outcomes if o["outcome"] == "soft_penalty"]
        penalty_total = round(sum(o["penalty"] for o in soft) * penalty_scale, 4)
        entry = {
            "title": m["title"], "year": m["year"], "genres": m["genres"], "runtime_minutes": m["runtime_minutes"],
            "mpa_rating": m["mpa_rating"], "franchise": m["franchise"], "director": m["director"],
            "taste_score": t["score"], "taste_breakdown": t["breakdown"],
            "penalty_total": penalty_total,
            "soft_penalties_applied": [{"rule_id": o["rule_id"], "name": o["name"], "penalty": round(o["penalty"] * penalty_scale, 4),
                                        "justification_type": o["justification_type"], "source": o["source"]} for o in soft],
            "final_score": round(t["score"] + penalty_total, 4),
            "rules_evaluated": [{"rule_id": o["rule_id"], "outcome": o["outcome"], "penalty": o["penalty"]} for o in outcomes],
            "flashing_tag": m["sensitivity_tags"]["flashing_strobe_content"],
            "weak_taste_match": bool(t["breakdown"]) and t["score"] < WEAK_TASTE,
            "warnings": [],
        }
        if entry["weak_taste_match"]:
            entry["warnings"].append("not a strong match for the chosen genres; added to fill the list")
        if m["runtime_minutes"] is None:
            entry["warnings"].append("runtime not listed")
        scored.append(entry)

    # highest score first; ties go alphabetically so the output is always the same
    scored.sort(key=lambda e: (-e["final_score"], e["title"]))

    # 4. top 5, with some variety
    if profile.get("diversity_rerank", True):
        top, div_log = _diversify(scored, k)
        top.sort(key=lambda e: (-e["final_score"], e["title"]))
    else:
        top, div_log = scored[:k], []

    # 5. final safety check: better to fail than to return a blocked movie
    movie_by_title = {m["title"]: m for m in movies}
    for e in top:
        if e["title"] in excluded_titles:
            raise VetoViolation(f"{e['title']} was removed earlier but ended up in the results")
        v = hard_violations(rules, profile, movie_by_title[e["title"]])
        if v:
            raise VetoViolation(f"{e['title']} breaks hard rules {v}")

    for i, e in enumerate(top, 1):
        e["rank"] = i
        e["explanation"] = explain(e, profile)

    n_weak = sum(1 for e in top if e["weak_taste_match"])
    if n_weak:
        warnings.append(f"{n_weak} of {len(top)} picks are a weak taste match: not many safe movies fit these genres")

    applicable_ids = sorted({o["rule_id"] for _, outs in eligible for o in outs} |
                            {r["rule_id"] for e in excluded for r in e["hard_rules_fired"]})
    all_ids = [r["rule_id"] for r in rules]
    return {
        "recommendations": top,
        "excluded_candidates": excluded,
        "rules_applicable_to_this_patient": applicable_ids,
        "rules_not_applicable_to_this_patient": [r for r in all_ids if r not in applicable_ids],
        "summary": {
            "candidates_considered": len(candidates),
            "hard_excluded": len(excluded),
            "eligible_after_veto": len(eligible),
            "eligible_with_soft_penalty": sum(1 for e in scored if e["penalty_total"] < 0),
        },
        "diversity": {"enabled": bool(profile.get("diversity_rerank", True)), "log": div_log},
        "audit": {"veto_check": "passed", "hard_rule_violations_in_results": 0},
        "warnings": warnings,
    }
