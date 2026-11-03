# Movie recommender for hospital patients

Hospitals often have screens in patient rooms, but picking what to show isn't as simple as it sounds. A film that's fine for one child can trigger a seizure in another, and a three-hour epic is a bad idea for someone exhausted from chemo.

This project takes a patient's profile and suggests five movies they'll enjoy, while making sure none of them could cause harm. Safety always comes first: a movie that breaks a safety rule is removed before taste is even considered.

## A quick example

A 9-year-old on chemotherapy, very tired, whose seizures can be triggered by flashing lights, and who loves comedy and cartoons:

```json
{
  "age": 9,
  "diagnosis_context": "pediatric_oncology",
  "treatment_phase": "active_high_fatigue",
  "known_sensitivities": ["photosensitive_seizure_trigger"],
  "preferred_genres": ["Comedy", "Animation"]
}
```

She gets **Despicable Me, Finding Dory, Inside Out, Ratatouille** and **Shrek**.

19 movies are taken out first, for example:
- *Incredibles 2*, because Disney warned cinemas about its strobe scenes
- *Toy Story 5*, because viewers reported flashing lights
- *The Fault in Our Stars*, because it's a story about a teenager with cancer

Each pick comes with a short explanation, for example:

> Taste match is 0.86 out of 1: matched 2/2 preferred genres: comedy, animation. Marked down because of: light-sensitive patient, no flashing known but not confirmed (R-04, my own reasoning) -0.15. Final score 0.71 (taste 0.86, markdowns -0.15).

## How it works

1. **Remove** every movie that a hard rule blocks for this patient.
2. **Score** the rest on how well they fit the patient's taste: genres, mood, and similarity to movies they already like.
3. **Subtract** penalties for things that aren't ideal, like a long film for someone who's very tired. The penalty is shown as its own number, so you can always see taste and safety separately.
4. **Pick** the top five, without repeating a franchise.
5. **Check** the final five against every hard rule once more before answering.

Since unsafe movies are gone before step 2, nothing later on (not a high taste score, not the variety step) can bring them back. The tests try hard to break this, and can't.

## Why plain code and not an AI model

With patients, I wanted to be able to promise that a blocked film never gets through, and to show exactly why each film was picked. Ordinary code does both: the same patient always gets the same answer, and every number can be traced back to a feature or a rule.

I also looked at the alternatives:
- **Letting an LLM rank the movies** would give nicer wording, but there's no way to prove it will always respect a safety rule.
- **Mixing everything into one score** would be simpler, but then a very high taste score could outweigh a safety concern.

So it's a hybrid: hard rules as a filter, then content-based scoring for taste, then penalties added separately.

## Running it

You need Python 3.9 or newer.

```bash
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m pytest -q                # 21 tests
python evaluation/run_eval.py      # runs 15 example patients
uvicorn recommender.api:app        # starts the API
```

Then open http://127.0.0.1:8000/docs, choose `POST /recommendations`, then "Try it out" and "Execute".

## The API

`POST /recommendations` takes the patient profile in the request body and returns:

- **recommendations**: the top 5, each with its taste score and what it was made of, the penalties applied, the final score, every rule that was checked and its result (pass, penalty or removed), and the explanation
- **excluded_candidates**: every movie that was removed, with the rule that removed it and that rule's source
- **audit**: the result of the final safety check

There's a full example in [`docs/sample_response.json`](docs/sample_response.json).

Other endpoints: `GET /rules` (every rule) and `GET /health`.

**Allowed values**
- `diagnosis_context`: `pediatric_oncology`, `adult_oncology`, `chronic_pediatric_illness`, `general_inpatient`, `other`
- `treatment_phase`: `active_high_fatigue`, `active_nausea`, `post_treatment_recovery`, `stable`
- `known_sensitivities`: `photosensitive_seizure_trigger`, `grief_sensitive`, `anxiety_sensitive`, `needs_subtitles`, `needs_audio_description`
- optional: `preferred_genres`, `preferred_tones`, `liked_titles`

A misspelt sensitivity returns an error instead of being quietly ignored.

## Where the data and rules come from

- **Movies**: 66 titles, from family classics to a few grown-up films. For each one there's the basics (genre, length, rating, director), plus the things that matter in a hospital: flashing scenes, how intense it is, and how easy the story is to follow. Runtime, rating and director for all 66 are checked against TMDB. See [`docs/DATA.md`](docs/DATA.md).
- **Rules**: 26 rules, built from the Epilepsy Foundation, Ofcom's flashing-image guidance, the MPA film rating rules, the American Cancer Society, and child-life guidelines from Stanford Children's and Children's Wisconsin. Each rule says whether it comes straight from a source, is based on one, or is my own reasoning. See [`docs/RULES.md`](docs/RULES.md).
- **Research notes**: what I looked up and what I decided, in [`docs/DECISIONS_LOG.md`](docs/DECISIONS_LOG.md).
- **Testing**: see [`docs/EVALUATION.md`](docs/EVALUATION.md).

## Project layout

```
data/          the movie list and the rules
recommender/   the code: rules, scoring, the pipeline, and the API
scripts/       build the movie data and check it against TMDB
tests/         safety and API tests
evaluation/    runs 15 example patients and checks the results
docs/          data, rules, research notes and evaluation
```
