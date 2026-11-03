"""Taste score: how well a movie matches what the patient likes, from 0 to 1.

This part knows nothing about safety. It only ever sees movies that are already allowed."""
from typing import Any, Dict, List, Optional, Set

# How much each part counts. If the patient leaves one out (e.g. no liked titles), the rest are scaled up.
BASE_WEIGHTS = {"genre_match": 0.40, "genre_focus": 0.15, "tone_match": 0.20, "similar_to_liked": 0.25}
NEUTRAL = 0.5  # used when the patient gives no preferences at all


def _tokens(m: Dict[str, Any]) -> Set[str]:
    return {f"g:{g.lower()}" for g in m["genres"]} | {f"t:{t.lower()}" for t in m.get("tones", [])}


def _jaccard(a: Set[str], b: Set[str]) -> float:
    return len(a & b) / len(a | b) if (a | b) else 0.0


def taste(profile: Dict[str, Any], movie: Dict[str, Any], liked_movies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Returns the score and how each part contributed. Every part is between 0 and 1."""
    feats: Dict[str, Dict[str, Any]] = {}

    pref_g = [g.lower() for g in profile["preferred_genres"]]
    if pref_g:
        have = {g.lower() for g in movie["genres"]}
        hit = [g for g in pref_g if g in have]
        feats["genre_match"] = {"raw": len(hit) / len(pref_g),
                                "detail": f"matched {len(hit)}/{len(pref_g)} preferred genres: {', '.join(hit) or 'none'}"}
        union = set(pref_g) | have
        feats["genre_focus"] = {"raw": len(set(pref_g) & have) / len(union),
                                "detail": f"how much of the film is the preferred genres ({len(set(pref_g) & have)} of {len(union)} genres overlap)"}

    pref_t = [t.lower() for t in profile["preferred_tones"]]
    if pref_t:
        have_t = {t.lower() for t in movie.get("tones", [])}
        hit_t = [t for t in pref_t if t in have_t]
        feats["tone_match"] = {"raw": len(hit_t) / len(pref_t),
                               "detail": f"matched {len(hit_t)}/{len(pref_t)} preferred tones: {', '.join(hit_t) or 'none'}"}

    if liked_movies:
        sims = [_jaccard(_tokens(movie), _tokens(l)) for l in liked_movies]
        feats["similar_to_liked"] = {"raw": sum(sims) / len(sims),
                                     "detail": "similar in genre and mood to " + ", ".join(l["title"] for l in liked_movies)}

    if not feats:
        return {"score": NEUTRAL, "breakdown": {}, "note": "no taste signal supplied; neutral 0.5 for every title"}

    total_w = sum(BASE_WEIGHTS[k] for k in feats)
    score = 0.0
    for k, f in feats.items():
        f["weight"] = round(BASE_WEIGHTS[k] / total_w, 4)
        f["contribution"] = round(f["raw"] * f["weight"], 4)
        f["raw"] = round(f["raw"], 4)
        score += f["contribution"]
    return {"score": round(score, 4), "breakdown": feats}
