"""Builds data/movies.json from data/curated_movies.py

Run:  python scripts/build_dataset.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data"))
from curated_movies import ROWS  # noqa: E402

FLASH = {"none", "mild", "confirmed_present", "unknown"}
INTENSITY = {"low", "medium", "high"}
PACING = {"simple", "moderate", "dense"}
MPA = {"G", "PG", "PG-13", "R", "NC-17"}


def load_ids():
    f = ROOT / "data" / "tmdb_ids.json"  # written by scripts/fetch_tmdb_ids.py
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def load_verified():
    f = ROOT / "data" / "verified_titles.txt"  # titles checked against TMDB / Wikipedia
    if not f.exists():
        return set()
    return {ln.strip() for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")}


def build(row, ids, verified):
    (title, year, runtime, mpa, genres, director, franchise,
     intensity, pacing, themes, tones, flash) = row
    f_val, f_src, f_url, f_conf, f_note = flash
    assert f_val in FLASH and intensity in INTENSITY and pacing in PACING and mpa in MPA, title
    return {
        "title": title,
        "year": year,
        "tmdb_id": ids.get(title),
        "genres": genres,
        "runtime_minutes": runtime,
        "mpa_rating": mpa,
        "director": director,
        "franchise": franchise,
        "tones": tones,
        "sensitivity_tags": {
            "flashing_strobe_content": f_val,
            "thematic_intensity": intensity,
            "pacing_complexity": pacing,
            "theme_flags": themes,
            "accessibility": {"subtitles_available": None, "audio_description_available": None},
        },
        "provenance": {
            "core_metadata": ({"source": "checked_against_tmdb_by_author", "metadata_verified": True} if title in verified
                              else {"source": "curated_list", "metadata_verified": False}),
            "flashing": {"source": f_src, "url": f_url, "confidence": f_conf, "note": f_note},
            "theme_pacing_tones": {"source": "general_knowledge", "confidence": "medium"},
            "accessibility": {"source": "not_listed", "confidence": "none"},
        },
        "tagging_source": f_src,
        "tagging_confidence": f_conf,
    }


def main():
    ids, verified = load_ids(), load_verified()
    unknown = verified - {r[0] for r in ROWS}
    if unknown:
        sys.exit(f"data/verified_titles.txt has titles that are not in the dataset (check spelling): {sorted(unknown)}")
    movies = [build(r, ids, verified) for r in ROWS]
    titles = [m["title"] for m in movies]
    assert len(titles) == len(set(titles)), "duplicate titles"
    out = ROOT / "data" / "movies.json"
    out.write_text(json.dumps(movies, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    n = len(movies)
    flash = Counter(m["sensitivity_tags"]["flashing_strobe_content"] for m in movies)
    print(f"Wrote {n} titles to {out}")
    print("Flashing tag distribution:", dict(flash))
    print("Flashing evidence confidence:", dict(Counter(m["tagging_confidence"] for m in movies)))
    print("Runtime missing:", [m["title"] for m in movies if m["runtime_minutes"] is None])
    print("tmdb_id filled:", sum(1 for m in movies if m["tmdb_id"]), "/", n)
    print("Metadata verified:", sum(1 for m in movies if m["provenance"]["core_metadata"]["metadata_verified"]), "/", n)
    print("Accessibility listed:", 0, "/", n)


if __name__ == "__main__":
    main()
