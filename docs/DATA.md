# The movie data

All 66 movies live in one place: [`data/curated_movies.py`](../data/curated_movies.py). It's a plain Python list, one movie per line, so it's easy to read and edit. When you run

```bash
python scripts/build_dataset.py
```

it turns that list into [`data/movies.json`](../data/movies.json), which is the file the recommender actually reads. If you ever change a movie, edit the list and run that command again. Don't edit the JSON by hand.

## Which movies, and why

I wanted both a sick child and an adult to get sensible picks, so the list is a mix:

- Pixar and Disney favourites, like *Toy Story*, *Finding Dory*, *Inside Out* and *Frozen*
- Studio Ghibli: *My Neighbor Totoro*, *Spirited Away*, *Ponyo*
- older classics like *The Wizard of Oz*, *Mary Poppins* and *Singin' in the Rain*
- two calm nature documentaries: *March of the Penguins* and *Winged Migration*
- grown-up films like *Forrest Gump*, *Interstellar* and *The Shawshank Redemption*

A few intense or R-rated films, like *The Conjuring* and *Saving Private Ryan*, are in there on purpose. They let me test that the rules really keep them away from children.

## What I note down for each movie

**The basics:** title, year, director, franchise, genres, runtime and US rating (G, PG, PG-13, R).

**How it feels:** a few tones such as *funny*, *heartwarming*, *calm* or *exciting*. Together with genres, these are what the taste score uses.

**The things that matter in a hospital:**

| Tag | Values | Why it matters |
|---|---|---|
| Flashing | `none`, `mild`, `confirmed_present`, `unknown` | can trigger seizures in light-sensitive patients |
| Intensity | `low`, `medium`, `high` | very intense films aren't great for children or anxious patients |
| Plot | `simple`, `moderate`, `dense` | a complicated plot is hard to follow when you're exhausted |
| Themes | e.g. `death_or_loss`, `violence`, `medical_care`, `scary_creatures` | some topics are upsetting for children in hospital, or for someone grieving |
| Accessibility | subtitles and audio description: yes, no, or not listed | for patients who need them |

Each movie also has a `provenance` section in `movies.json`, so you can always see where a piece of information came from and how sure it is.

## Flashing scenes

This is the tag I care about most, because getting it wrong could cause a seizure. Here's how each value is used:

- **`confirmed_present`**: a public source reports strobe or flashing. *Incredibles 2* is the clearest example. In June 2018 Disney asked cinemas to put up warnings, because one scene has more than 90 seconds of strobe ([Slashfilm](https://www.slashfilm.com/incredibles-2-warning/)).
- **`mild`**: some minor flashing reported. *Toy Story 5* scored 6/10 for flashing on [Movie Health Community](https://moviehealthcommunity.tumblr.com/tagged/Photosensitive%20Epilepsy), a site that rates films for photosensitive viewers. It mentions camera flashes and flickering lights.
- **`none`**: no known flashing scenes.
- **`unknown`**: we don't know either way. These are mostly action films with lots of explosions, lasers or bright effects.

For a light-sensitive patient, anything that isn't `none` is removed, and that includes `unknown`. If I'm not sure a film is safe, I'd rather leave it out.

## Checked against TMDB

Every movie's runtime, rating and director has been checked against [TMDB](https://www.themoviedb.org/), and each record has its TMDB ID. On 3 November 2026:

- 50 of the 66 matched straight away.
- 10 runtimes were 1–3 minutes off, so I updated them to TMDB's numbers. None of them crossed the 2-hour or 2.5-hour line, so no recommendation changed.
- *WALL-E* and *Wonder* were first matched to the wrong films (a short, and *Wonder Woman*). I fixed the script so an exact title match wins, and both now match.
- Four films list a different director on TMDB because they have two: *Big Hero 6*, *Minions*, *Encanto* and *Avengers: Endgame*. Both names are correct, so I kept mine.
- *Harry Potter* uses its US title, *Sorcerer's Stone*. TMDB uses the UK one, *Philosopher's Stone*. It's the same film.

All 66 now show `metadata_verified: true` in `movies.json`.

### Running the check again

If you add or change movies, run it again with your own free API key from TMDB:

```bash
export TMDB_API_KEY=your_key
python scripts/fetch_tmdb_ids.py
```

It prints `OK` or `DIFF` for every movie and saves the details to `data/tmdb_check.json`. Then:

1. fix anything that's wrong in `data/curated_movies.py`
2. add the titles you've checked to `data/verified_titles.txt`, one per line
3. run `python scripts/build_dataset.py` again
