"""Writes the short "why this movie" sentence from the scores and rules already worked out."""
from typing import Any, Dict

BACKING = {
    "sourced": "backed by a source",
    "inferred_from_source": "partly backed by a source",
    "inferred": "my own reasoning",
}


def explain(entry: Dict[str, Any], profile: Dict[str, Any]) -> str:
    parts = []
    bd = entry["taste_breakdown"]
    if bd:
        reasons = [bd[k]["detail"] for k in ("genre_match", "tone_match", "similar_to_liked") if k in bd]
        parts.append(f"Taste match is {entry['taste_score']:.2f} out of 1: " + "; ".join(reasons) + ".")
    else:
        parts.append("No taste preferences were given, so every movie gets a neutral 0.50 taste score "
                     "and ties are broken alphabetically.")

    if entry["soft_penalties_applied"]:
        notes = [f"{p['name'].lower()} ({p['rule_id']}, {BACKING[p['justification_type']]}) {p['penalty']:+.2f}"
                 for p in entry["soft_penalties_applied"]]
        parts.append("Marked down because of: " + "; ".join(notes) + ".")
    else:
        parts.append("Nothing counted against it.")

    parts.append(f"Final score {entry['final_score']:.2f} "
                 f"(taste {entry['taste_score']:.2f}, markdowns {entry['penalty_total']:+.2f}).")
    return " ".join(parts)
