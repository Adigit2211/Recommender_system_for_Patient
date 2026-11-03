# Rules

These are the 26 rules the recommender uses. The full version, with the exact conditions the code checks, is in [`data/rules.json`](../data/rules.json).

There are two kinds:

- **Remove**: the movie is taken out for this patient, whatever else is true about it.
- **Penalty**: the movie stays, but points are taken off its score so it ranks lower. Taste scores go from 0 to 1, so -0.15 is a small nudge and -0.5 is a big drop.

Each rule also says where it came from: straight from a **source**, **based on a source** (a real guideline I applied to films), or **my reasoning**.

| ID | Rule | What happens | Where it came from | Why |
|---|---|---|---|---|
| R-01 | Light-sensitive patient, film has flashing | Remove | Source | Flashing can set off seizures in people with photosensitive epilepsy, so these films are removed outright. |
| R-02 | Light-sensitive patient, flashing unknown | Remove | Based on source | If we don't know whether a film has flashing, we don't risk it for this patient. |
| R-03 | Light-sensitive patient, minor flashing reported | Remove | Based on source | Even minor reported flashing is removed for this patient; the risk isn't worth one extra film. |
| R-04 | Light-sensitive patient, no flashing known but not confirmed | Penalty -0.15 | My reasoning | Films with stronger evidence of no flashing rank slightly above ones without it. |
| R-05 | Under 17, R-rated film | Remove | Based on source | R-rated films are kept away from under-17s in a hospital setting, where no parent may be present to decide. |
| R-06 | Under 18, NC-17 film | Remove | Source | Follows the rating board's own rule: nobody 17 or under. |
| R-07 | Under 13, PG-13 film | Penalty -0.25 | Source | PG-13 films can still be shown to under-13s, but rank lower. |
| R-08 | Seriously ill child, film about serious illness | Remove | Based on source | A child going through serious illness shouldn't be shown a film that is centred on serious illness. |
| R-09 | Adult with cancer, film about serious illness | Penalty -0.50 | My reasoning | Adults can choose for themselves, so this is a strong penalty rather than a removal. |
| R-10 | Child in hospital, hospital or medical scenes | Penalty -0.30 | Based on source | Hospital and medical scenes rank lower for children who are already in hospital. |
| R-11 | Child in hospital, illness subplot | Penalty -0.20 | Based on source | An illness subplot is lighter than a whole film about it, so the penalty is smaller. |
| R-12 | Child in hospital, death or loss | Penalty -0.30 | Based on source | Death and loss rank lower for children, but these films aren't removed, since many classics include them. |
| R-13 | Child in hospital, violence | Penalty -0.20 | Based on source | Violent themes rank lower for children in hospital. |
| R-14 | Child in hospital, very intense film | Penalty -0.35 | Based on source | Very intense films rank lower for children in hospital. |
| R-15 | Young child, scary creatures | Penalty -0.20 | My reasoning | Scary creatures rank lower for young children. |
| R-16 | Bereaved patient, death or loss | Remove | My reasoning | The patient has said this topic upsets them, so these films are removed. |
| R-17 | Anxious patient, scary or intense film | Penalty -0.40 | My reasoning | Scary, gory or very intense films rank well down for patients with anxiety. |
| R-18 | Very tired patient, film over 2.5 hours | Penalty -0.35 | My reasoning | Very long films are hard to sit through when exhausted; they rank lower but can still be paused and finished. |
| R-19 | Very tired patient, film over 2 hours | Penalty -0.15 | My reasoning | A smaller penalty for films that are long but not very long. |
| R-20 | Very tired patient, complicated plot | Penalty -0.25 | My reasoning | Complicated plots are hard to follow when tired. |
| R-21 | Very tired patient, length not listed | Penalty -0.10 | My reasoning | A small penalty when a film's length isn't listed. |
| R-22 | Nauseous patient, gory scenes | Penalty -0.40 | My reasoning | Gory scenes rank well down for patients feeling sick from treatment. |
| R-23 | Nauseous patient, very intense film | Penalty -0.20 | My reasoning | Intense films rank lower for patients feeling sick from treatment. |
| R-24 | Needs subtitles, subtitles not listed | Penalty -0.20 | My reasoning | Films rank slightly lower when subtitle availability isn't listed. |
| R-25 | Needs subtitles, film has none | Remove | My reasoning | If a film definitely has no subtitles, it's removed for patients who need them. |
| R-26 | Needs audio description, not listed | Penalty -0.20 | My reasoning | Films rank slightly lower when audio description availability isn't listed. |

## Sources

| Short name | Source |
|---|---|
| EF | [Epilepsy Foundation, Photosensitivity and Seizures](https://www.epilepsy.com/what-is-epilepsy/seizure-triggers/photosensitivity) |
| ITC | [ITC Guidance Note on Flashing Images and Regular Patterns in Television (hosted by Ofcom, rev. July 2001), paras 2, 3, 3.1.1](https://www.ofcom.org.uk/__data/assets/pdf_file/0021/16248/gn_flash.pdf) |
| OFCOM212 | [Ofcom Broadcasting Code Rule 2.12, quoted in Ofcom Broadcast Bulletin 178](https://www.ofcom.org.uk/siteassets/resources/documents/about-ofcom/bulletins/broadcast-bulletins/archive/obb178/obb178.pdf) |
| MPA | [MPA Classification and Rating Rules, Section 3(C), pp. 7-8](https://www.filmratings.com/wp-content/uploads/2025/08/rating_rules.pdf) |
| ACS | [American Cancer Society, Getting Help for Fatigue](https://www.cancer.org/content/dam/cancer-org/cancer-control/en/what-to-do/getting-help-for-fatigue.pdf) |
| STAN | [Stanford Children's Child Life Entertainment/Special Events Guidelines, items 5, 10, 12](https://www.stanfordchildrens.org/content/dam/sch/content-public/pdf/Event_Guidelines.pdf) |
| CWI | [Children's Wisconsin Entertainment and Visitor Guidelines (3/19/2021), 'The Day of your Visit' items 1 and 6](https://childrenswi.org/-/media/chwlibrary/files/patient-family-experience/cl-entertainment-guidelines.pdf) |
