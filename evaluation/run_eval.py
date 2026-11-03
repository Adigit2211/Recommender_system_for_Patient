"""Runs 15 made-up patients through the recommender and checks the results.

    python evaluation/run_eval.py

For every patient it checks that none of the 5 picks breaks a safety rule, in two ways:
the recommender's own final check, and a separate hand-written check below that doesn't use data/rules.json.
It also shows how different the lists are between patients, and what the rules changed for each one.

Writes evaluation/results.json and evaluation/results.md.
"""
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from recommender.engine import load_movies, recommend  # noqa: E402

MOVIES = {m["title"]: m for m in load_movies()}


def patient(pid, desc, age, dx, phase, sens=(), genres=(), tones=(), liked=()):
    return {"id": pid, "desc": desc, "profile": {
        "age": age, "diagnosis_context": dx, "treatment_phase": phase, "known_sensitivities": list(sens),
        "preferred_genres": list(genres), "preferred_tones": list(tones), "liked_titles": list(liked), "diversity_rerank": True}}


PATIENTS = [
    patient("P01", "9, cancer treatment, very tired, flashing lights trigger seizures", 9, "pediatric_oncology", "active_high_fatigue", ["photosensitive_seizure_trigger"], ["Comedy", "Animation"]),
    patient("P02", "6, cancer treatment, nauseous, anxious", 6, "pediatric_oncology", "active_nausea", ["anxiety_sensitive"], ["Animation", "Family"], ["calm", "heartwarming"]),
    patient("P03", "15, recovering from cancer, recently bereaved", 15, "pediatric_oncology", "post_treatment_recovery", ["grief_sensitive"], ["Drama", "Comedy"], [], ["Forrest Gump"]),
    patient("P04", "12, long-term illness, photosensitive, needs subtitles", 12, "chronic_pediatric_illness", "stable", ["photosensitive_seizure_trigger", "needs_subtitles"], ["Adventure", "Fantasy"]),
    patient("P05", "45, cancer treatment, very tired", 45, "adult_oncology", "active_high_fatigue", [], ["Drama", "Comedy"], ["thoughtful"]),
    patient("P06", "62, cancer treatment, nauseous, likes action", 62, "adult_oncology", "active_nausea", [], ["Action", "Thriller"]),
    patient("P07", "30, in hospital, photosensitive, likes sci-fi and action", 30, "general_inpatient", "stable", ["photosensitive_seizure_trigger"], ["Science Fiction", "Action"]),
    patient("P08", "8, in hospital, very tired, loves Frozen", 8, "general_inpatient", "active_high_fatigue", [], ["Fantasy", "Music"], ["magical"], ["Frozen"]),
    patient("P09", "16, cancer treatment, very tired, likes horror", 16, "pediatric_oncology", "active_high_fatigue", [], ["Horror", "Thriller"]),
    patient("P10", "10, cancer treatment, bereaved and anxious", 10, "pediatric_oncology", "stable", ["grief_sensitive", "anxiety_sensitive"], ["Adventure", "Animation"]),
    patient("P11", "70, recovering from cancer, needs audio description", 70, "adult_oncology", "post_treatment_recovery", ["needs_audio_description"], ["Documentary", "Drama"]),
    patient("P12", "11, long-term illness, nauseous, photosensitive, bereaved", 11, "chronic_pediatric_illness", "active_nausea", ["photosensitive_seizure_trigger", "grief_sensitive"], ["Comedy", "Family"]),
    patient("P13", "35, very tired, likes long sci-fi", 35, "other", "active_high_fatigue", [], ["Science Fiction", "Adventure"]),
    patient("P14", "14, recovering from cancer, likes action", 14, "pediatric_oncology", "post_treatment_recovery", [], ["Action", "Adventure", "Science Fiction"]),
    patient("P15", "30, no restrictions, same taste as P01 (for comparison)", 30, "other", "stable", [], ["Comedy", "Animation"]),
]


def hand_check(p, m):
    """The main safety rules, written out by hand. Returns a list of problems (empty = fine)."""
    t, problems = m["sensitivity_tags"], []
    if "photosensitive_seizure_trigger" in p["known_sensitivities"] and t["flashing_strobe_content"] != "none":
        problems.append("flashing content for a photosensitive patient")
    if p["age"] < 17 and m["mpa_rating"] == "R":
        problems.append("R-rated film for under-17")
    if p["age"] < 18 and m["mpa_rating"] == "NC-17":
        problems.append("NC-17 film for under-18")
    if "grief_sensitive" in p["known_sensitivities"] and "death_or_loss" in t["theme_flags"]:
        problems.append("death/loss theme for a bereaved patient")
    if p["age"] < 18 and p["diagnosis_context"] in ("pediatric_oncology", "chronic_pediatric_illness") \
            and "central_serious_illness" in t["theme_flags"]:
        problems.append("illness-centred film for a seriously ill child")
    if "needs_subtitles" in p["known_sensitivities"] and t["accessibility"]["subtitles_available"] is False:
        problems.append("no subtitles for a patient who needs them")
    return problems


def titles(result):
    return [e["title"] for e in result["recommendations"]]


def overlap(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 1.0


def main():
    rows, picks = [], {}
    for item in PATIENTS:
        p = item["profile"]
        r = recommend(p)
        top = titles(r)
        picks[item["id"]] = top
        problems = {t: hand_check(p, MOVIES[t]) for t in top}
        without_rules = titles(recommend(p, rule_data={"rules": []}))
        rows.append({
            "id": item["id"], "patient": item["desc"], "top5": top,
            "scores": [(e["taste_score"], e["penalty_total"], e["final_score"]) for e in r["recommendations"]],
            "final_check": r["audit"]["veto_check"],
            "problems_found": {t: v for t, v in problems.items() if v},
            "removed_by_rules": r["summary"]["hard_excluded"],
            "still_allowed": r["summary"]["eligible_after_veto"],
            "taken_out_of_top5_by_rules": [t for t in without_rules if t not in top],
        })

    pairs = list(itertools.combinations(picks, 2))
    summary = {
        "patients": len(PATIENTS),
        "picks_that_break_a_rule": sum(len(r["problems_found"]) for r in rows),
        "final_checks_passed": sum(r["final_check"] == "passed" for r in rows),
        "different_movies_across_all_picks": len({t for top in picks.values() for t in top}),
        "average_overlap_between_two_patients": round(sum(overlap(picks[a], picks[b]) for a, b in pairs) / len(pairs), 3),
    }
    (ROOT / "evaluation" / "results.json").write_text(json.dumps({"summary": summary, "patients": rows}, indent=2) + "\n", encoding="utf-8")

    md = ["# Evaluation results", "", "Generated by `python evaluation/run_eval.py`.", "",
          f"- Patients tested: **{summary['patients']}**",
          f"- Picks that break a safety rule: **{summary['picks_that_break_a_rule']}**",
          f"- Final safety checks passed: **{summary['final_checks_passed']} / {summary['patients']}**",
          f"- Different movies across all {5 * summary['patients']} picks: **{summary['different_movies_across_all_picks']}**",
          "", "| ID | Patient | Removed | Top 5 (taste / penalty -> final) | Rules kept out of their top 5 |", "|---|---|---|---|---|"]
    for r in rows:
        cells = "<br>".join(f"{t} ({s[0]:.2f} / {s[1]:+.2f} -> {s[2]:.2f})" for t, s in zip(r["top5"], r["scores"]))
        md.append(f"| {r['id']} | {r['patient']} | {r['removed_by_rules']} | {cells} | {', '.join(r['taken_out_of_top5_by_rules']) or '-'} |")
    (ROOT / "evaluation" / "results.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    for r in rows:
        print(f"{r['id']}  {', '.join(r['top5'])}")
    if summary["picks_that_break_a_rule"] or summary["final_checks_passed"] != len(PATIENTS):
        sys.exit("A pick broke a safety rule")


if __name__ == "__main__":
    main()
