# Testing

I made up 15 patients covering every kind of rule: light sensitivity, grief, anxiety, age ratings, serious illness, tiredness, nausea and accessibility. One of them, P15, has no restrictions at all, so I could compare the others against it. Then I ran each one through the recommender.

To rerun it:

```bash
python evaluation/run_eval.py
```

The full results, with every patient's five picks and scores, are in [`evaluation/results.md`](../evaluation/results.md).

## Does anything unsafe get through?

No. **0 of the 75 picks broke a safety rule.**

I checked this two ways:
1. The recommender's own final check, which re-tests every pick against every hard rule before answering. It passed for all 15 patients.
2. A separate check in `run_eval.py`, written out by hand. It doesn't use the rules file at all, so a mistake in that file would still be caught.

The tests in `tests/test_veto.py` also try to sneak a removed movie back in on purpose:
- giving it a huge taste score
- slipping it in during the variety step
- breaking the first filter entirely

Each time, it's stopped. Changing the penalty sizes doesn't change which movies get removed either.

## Do people still get movies they'd like?

Yes. Across the 15 patients there are **41 different movies** in the 75 picks, and on average two patients share very few picks (overlap 0.07). Each list follows that patient's own tastes.

A few examples:

**P01: 9, on chemo, very tired, light-sensitive, likes comedy and animation.** 19 movies are removed. She gets *Despicable Me, Finding Dory, Inside Out, Ratatouille, Shrek*. Compared with P15, who has the same taste and no restrictions, the rules swapped out only *Big Hero 6* and *Cars*, because their flashing status is unknown.

**P03: 15, recovering from cancer, recently bereaved, likes drama and comedy, enjoyed *Forrest Gump*.** 22 movies are removed, mostly films about death or loss, like *Finding Nemo*, *Up* and *Coco*. He gets *Mrs. Doubtfire, La La Land, Groundhog Day, The Princess Diaries, Mamma Mia!*. These are warm, funny films that still match his taste.

**P04: 12, long-term illness, light-sensitive, needs subtitles, likes adventure and fantasy.** She gets *Paddington, Ponyo, The Wizard of Oz, Luca, How to Train Your Dragon*. Without the rules, *Harry Potter* and *The Lord of the Rings* would have been in her list. *The Lord of the Rings* is removed because its flashing is unknown, and *Harry Potter* drops down because of its darker themes.

**P08: 8, very tired, loves *Frozen*, likes fantasy and music.** He gets *Encanto, Mary Poppins, Dumbo, The Wizard of Oz, Coco*. These are musical, magical films, just like *Frozen*.

## Where the rules come from

Of the 26 rules, 3 come straight from a source, 9 are based on a source, and 14 are my own reasoning. Each one is labelled, so you can see the basis for every decision the recommender makes. The details are in [`RULES.md`](RULES.md).
