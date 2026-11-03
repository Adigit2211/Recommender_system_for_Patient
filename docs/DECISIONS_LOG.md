# Research notes

What I looked up, what I found, and what I decided. Dates are in IST.

## Looking for guidelines (29 October 2026)

**Epilepsy Foundation, [photosensitivity page](https://www.epilepsy.com/what-is-epilepsy/seizure-triggers/photosensitivity).** About 3% of people with epilepsy are photosensitive. It's more common in children and teenagers, and 5–30 flashes per second is the most risky range. Contrasting stripes can also be a trigger.
→ This is the basis of the flashing rule (R-01).

**Ofcom / ITC [flashing images guidance](https://www.ofcom.org.uk/__data/assets/pdf_file/0021/16248/gn_flash.pdf).** These are the UK TV rules. A harmful flash is a big jump in brightness, and more than three flashes in one second over a quarter of the screen isn't allowed. Saturated red flashes are risky too, and long flashing sequences can be a risk even within the limits. Rule 2.12 of the Broadcasting Code asks broadcasters to keep the risk to photosensitive viewers low.
→ This is why unknown flashing is treated as unsafe (R-02), and why even minor flashing is removed (R-03).

**MPA [rating rules](https://www.filmratings.com/wp-content/uploads/2025/08/rating_rules.pdf), pages 7–8.** PG-13: "Parents Strongly Cautioned. Some Material May Be Inappropriate For Children Under 13." R: "Children Under 17 Require Accompanying Parent or Adult Guardian." NC-17: "No One 17 and Under Admitted."
→ Age rules R-05, R-06, R-07.

**American Cancer Society, [Getting Help for Fatigue](https://www.cancer.org/content/dam/cancer-org/cancer-control/en/what-to-do/getting-help-for-fatigue.pdf).** Cancer fatigue doesn't go away with rest, and people find it hard to focus. The advice is to save energy for what matters most. It doesn't talk about films.
→ I made the link to film length and plot complexity myself (R-18 to R-21).

**Stanford Children's [entertainment guidelines](https://www.stanfordchildrens.org/content/dam/sch/content-public/pdf/Event_Guidelines.pdf)** and **Children's Wisconsin [visitor guidelines](https://childrenswi.org/-/media/chwlibrary/files/patient-family-experience/cl-entertainment-guidelines.pdf).** Both are written for people visiting to entertain children in hospital. They say to avoid themes like death, violence, illness and medical care, to keep sessions short (20–40 minutes), and to take care not to frighten children.
→ Applied to films as the theme rules (R-08, R-10 to R-14).

## Looking for flashing information on specific films

- Searched for films with flashing warnings. *Incredibles 2* came up straight away: Disney asked cinemas to put up warnings in June 2018 ([Slashfilm](https://www.slashfilm.com/incredibles-2-warning/)).
- Found [Movie Health Community](https://moviehealthcommunity.tumblr.com/tagged/Photosensitive%20Epilepsy), which rates new films for flashing. *Toy Story 5* is on it, at 6/10.
- I couldn't find a big database covering older films. So films with no known flashing are tagged `none`, and action-heavy ones are tagged `unknown`, which the system treats as unsafe.

## Decisions

- **Hard vs soft.** Anything that could cause real harm (seizures, age-restricted content, a topic the patient said upsets them) removes the film. Things that just make a film a worse fit (long, complicated, intense) only lower its score.
- **Unknown flashing counts as unsafe.** For a seizure risk, I'd rather lose a few films than take a chance.
- **No AI model in the ranking.** I wanted the safety rules to be guaranteed in code and every pick to be explainable. Explanations are built from the scores themselves.
- **Penalty sizes.** Taste goes from 0 to 1. I used -0.1 to -0.15 for small nudges, -0.2 to -0.3 for a clear drop, and -0.35 to -0.5 when it should fall well down the list.
- **Variety.** At most one film per franchise and two per director in the top five, so a fan of Pixar doesn't get five Toy Story films.
- **Toy Story 5.** Checked on [Wikipedia](https://en.wikipedia.org/wiki/Toy_Story_5): 102 minutes, PG, directed by Andrew Stanton.

## Checking the movies against TMDB (3 November 2026)

- My network cut the connection to `api.themoviedb.org`, but TMDB's other address, `api.tmdb.org`, worked. I switched the script to that.
- First run: 50 of 66 matched. Two were matched to the wrong film: *WALL-E* got a short film (TMDB spells it "WALL·E"), and *Wonder* got *Wonder Woman*. I changed the script to prefer an exact title match, and both then matched.
- I updated 10 runtimes that were 1–3 minutes off: *Zootopia, Kung Fu Panda, The Lion King, Ponyo, Soul, Paddington 2, The Princess Bride, The Martian, La La Land* and *The Fellowship of the Ring*.
- Final run: 61 OK, 5 different. Four are co-directed films where TMDB lists the other director (*Big Hero 6, Minions, Encanto, Avengers: Endgame*). The fifth is *Harry Potter*'s US title. All five are correct as they are.
- All 66 are now marked `metadata_verified: true`. The tests and the 15-patient check gave the same results as before.
