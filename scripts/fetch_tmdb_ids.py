"""Checks every movie against TMDB and saves the TMDB IDs."""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.tmdb.org/3"  


def get(path, retries=4, **params):
    """One TMDB request, retried with growing waits (1, 2, 4 s) if the connection is dropped."""
    for attempt in range(retries):
        try:
            return _get_once(path, **params)
        except urllib.error.HTTPError:
            raise  
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)


def _get_once(path, **params):
    headers = {"accept": "application/json"}
    if os.environ.get("TMDB_READ_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["TMDB_READ_TOKEN"]
    else:
        params["api_key"] = os.environ["TMDB_API_KEY"]
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as r:
        return json.load(r)


def us_rating(detail):
    for entry in detail.get("release_dates", {}).get("results", []):
        if entry.get("iso_3166_1") == "US":
            dates = [d for d in entry.get("release_dates", []) if d.get("certification")]
            theatrical = [d for d in dates if d.get("type") == 3]
            pick = (theatrical or dates or [{}])[0]
            return pick.get("certification") or None
    return None


def director(detail):
    names = [c["name"] for c in detail.get("credits", {}).get("crew", []) if c.get("job") == "Director"]
    return names[0] if names else None


def simple(title):
    """Lowercase letters and digits only, so small spelling differences don't matter."""
    return re.sub(r"[^a-z0-9]", "", title.lower())


def check_one(m):
    """Returns (tmdb_id or None, row dict)."""
    res = get("/search/movie", query=m["title"], year=m["year"]).get("results", [])
    same_year = [r for r in res if (r.get("release_date") or "")[:4] == str(m["year"])]
    if not same_year:
        return None, {"title": m["title"], "status": "NO MATCH", "note": "no TMDB result with this title and year"}
    # prefer an exact title match ("WALL-E" = "WALL·E"), so "Wonder" doesn't pick "Wonder Woman";
    # otherwise take the best-known film with that year
    exact = [r for r in same_year if simple(r.get("title", "")) == simple(m["title"])]
    hit = max(exact or same_year, key=lambda r: r.get("vote_count", 0))
    d = get(f"/movie/{hit['id']}", append_to_response="credits,release_dates")
    ours = {"runtime": m["runtime_minutes"], "rating": m["mpa_rating"], "director": m["director"]}
    theirs = {"runtime": d.get("runtime") or None, "rating": us_rating(d), "director": director(d)}
    diffs = {}
    if ours["runtime"] != theirs["runtime"]:
        diffs["runtime"] = (ours["runtime"], theirs["runtime"])
    if theirs["rating"] and ours["rating"] != theirs["rating"]:
        diffs["rating"] = (ours["rating"], theirs["rating"])
    if theirs["director"] and ours["director"] != theirs["director"]:
        diffs["director"] = (ours["director"], theirs["director"])
    if simple(d.get("title", "")) != simple(m["title"]):
        diffs["title"] = (m["title"], d.get("title"))
    return hit["id"], {"title": m["title"], "tmdb_id": hit["id"], "tmdb_title": d.get("title"),
                       "status": "DIFF" if diffs else "OK", "differences": diffs, "ours": ours, "tmdb": theirs}


def main():
    if not (os.environ.get("TMDB_API_KEY") or os.environ.get("TMDB_READ_TOKEN")):
        sys.exit("Set TMDB_API_KEY (or TMDB_READ_TOKEN) first. Use your own key; never commit it.")
    try:
        get("/configuration")
    except urllib.error.HTTPError as e:
        sys.exit(f"TMDB answered with HTTP {e.code}. If 401: the key is wrong or not activated yet.")
    except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
        sys.exit("Could not connect to api.themoviedb.org after 4 tries "
                 f"({e}).\nYour network may be blocking TMDB. Try a different network (e.g. a phone hotspot) "
                 "or a VPN, then run this again.")
    movies = json.loads((ROOT / "data" / "movies.json").read_text(encoding="utf-8"))
    ids, rows = {}, []
    for m in movies:
        try:
            tid, row = check_one(m)
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            tid, row = None, {"title": m["title"], "status": "ERROR", "note": str(e)}
        if tid:
            ids[m["title"]] = tid
        rows.append(row)
        time.sleep(0.1)
        diffs = "; ".join(f"{k}: ours {a!r} vs TMDB {b!r}" for k, (a, b) in row.get("differences", {}).items())
        print(f"{row['status']:9} {m['title']}  {diffs or row.get('note', '')}")
    (ROOT / "data" / "tmdb_ids.json").write_text(json.dumps(ids, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "data" / "tmdb_check.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ok = sum(r["status"] == "OK" for r in rows)
    print(f"\n{ok} OK, {sum(r['status'] == 'DIFF' for r in rows)} differ, "
          f"{sum(r['status'] in ('NO MATCH', 'ERROR') for r in rows)} not matched. IDs saved: {len(ids)}/{len(movies)}.")
    print("Next: fix wrong values in data/curated_movies.py, list titles you checked in data/verified_titles.txt, "
          "then run python scripts/build_dataset.py")


if __name__ == "__main__":
    main()
