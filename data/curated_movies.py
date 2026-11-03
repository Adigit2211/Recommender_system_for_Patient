"""The movie list. scripts/build_dataset.py turns this into data/movies.json

Each row: title, year, runtime (minutes), US rating, genres, director, franchise,
thematic intensity, how complex the plot is, theme flags, tones, and flashing info.

Flashing values:
    confirmed_present  a public source reports strobe/flashing sequences
    mild               minor flashes or flicker reported
    none               no known flashing scenes
    unknown            not known either way (treated as unsafe for photosensitive patients)
"""

SLASH = "https://www.slashfilm.com/incredibles-2-warning/"
MHC = "https://moviehealthcommunity.tumblr.com/tagged/Photosensitive%20Epilepsy"

# Flashing presets: (value, source, link, confidence, note)
NONE = ("none", "general_knowledge", None, "low", "No known flashing scenes.")
UNK  = ("unknown", "general_knowledge", None, "low", "Flashing not known; lots of action or bright effects.")
INC2 = ("confirmed_present", "news_report", SLASH, "high",
        "Disney asked cinemas to post a strobe warning in June 2018; one scene has over 90 seconds of strobe.")
TS5  = ("mild", "community_site", MHC, "medium",
        "Movie Health Community rated it 6/10 for flashing: camera flashes and flickering lights.")

# (title, year, runtime, mpa, genres, director, franchise, intensity, pacing, themes, tones, flash)
ROWS = [
    ("Toy Story", 1995, 81, "G", ["Animation", "Comedy", "Adventure", "Family"], "John Lasseter", "Toy Story", "low", "simple", ["peril"], ["funny", "heartwarming", "adventurous"], NONE),
    ("Toy Story 3", 2010, 103, "G", ["Animation", "Comedy", "Adventure", "Family"], "Lee Unkrich", "Toy Story", "medium", "moderate", ["peril", "abandonment"], ["heartwarming", "adventurous", "funny"], NONE),
    ("Toy Story 5", 2026, 102, "PG", ["Animation", "Comedy", "Adventure", "Family"], "Andrew Stanton", "Toy Story", "low", "simple", [], ["funny", "adventurous"], TS5),
    ("Finding Nemo", 2003, 100, "G", ["Animation", "Adventure", "Comedy", "Family"], "Andrew Stanton", "Finding Nemo", "medium", "simple", ["death_or_loss", "peril", "scary_creatures"], ["adventurous", "heartwarming", "funny"], NONE),
    ("Finding Dory", 2016, 97, "PG", ["Animation", "Adventure", "Comedy", "Family"], "Andrew Stanton", "Finding Nemo", "low", "simple", ["peril"], ["heartwarming", "funny", "adventurous"], NONE),
    ("Inside Out", 2015, 95, "PG", ["Animation", "Comedy", "Family", "Adventure"], "Pete Docter", "Inside Out", "medium", "moderate", ["emotional_sadness"], ["thoughtful", "heartwarming", "funny"], NONE),
    ("Up", 2009, 96, "PG", ["Animation", "Adventure", "Comedy", "Family"], "Pete Docter", "Up", "medium", "simple", ["death_or_loss"], ["heartwarming", "adventurous", "funny"], NONE),
    ("Coco", 2017, 105, "PG", ["Animation", "Adventure", "Family", "Music", "Fantasy"], "Lee Unkrich", "Coco", "medium", "moderate", ["death_or_loss"], ["musical", "heartwarming", "magical"], NONE),
    ("The Incredibles", 2004, 115, "PG", ["Animation", "Action", "Adventure", "Family"], "Brad Bird", "The Incredibles", "medium", "moderate", ["violence", "peril"], ["exciting", "funny", "adventurous"], UNK),
    ("Incredibles 2", 2018, 118, "PG", ["Animation", "Action", "Adventure", "Family"], "Brad Bird", "The Incredibles", "medium", "moderate", ["violence", "peril"], ["exciting", "funny", "adventurous"], INC2),
    ("Spider-Man: Into the Spider-Verse", 2018, 117, "PG", ["Animation", "Action", "Adventure", "Science Fiction"], "Bob Persichetti", "Spider-Man", "medium", "dense", ["violence", "peril", "death_or_loss"], ["exciting", "funny"], UNK),
    ("Big Hero 6", 2014, 102, "PG", ["Animation", "Action", "Comedy", "Family"], "Don Hall", "Big Hero 6", "medium", "moderate", ["death_or_loss", "peril"], ["heartwarming", "exciting", "funny"], UNK),
    ("Frozen", 2013, 102, "PG", ["Animation", "Adventure", "Comedy", "Family", "Music"], "Chris Buck", "Frozen", "medium", "simple", ["death_or_loss", "peril"], ["musical", "magical", "heartwarming"], NONE),
    ("Moana", 2016, 107, "PG", ["Animation", "Adventure", "Comedy", "Family", "Music"], "Ron Clements", "Moana", "medium", "simple", ["peril", "scary_creatures", "death_or_loss"], ["musical", "adventurous"], NONE),
    ("Zootopia", 2016, 109, "PG", ["Animation", "Adventure", "Comedy", "Crime", "Family"], "Byron Howard", "Zootopia", "low", "moderate", ["peril"], ["funny", "thoughtful", "adventurous"], NONE),
    ("Shrek", 2001, 90, "PG", ["Animation", "Comedy", "Fantasy", "Family"], "Andrew Adamson", "Shrek", "low", "simple", [], ["funny", "magical"], NONE),
    ("How to Train Your Dragon", 2010, 98, "PG", ["Animation", "Fantasy", "Adventure", "Family"], "Chris Sanders", "How to Train Your Dragon", "medium", "moderate", ["peril", "violence"], ["adventurous", "heartwarming", "exciting"], NONE),
    ("Kung Fu Panda", 2008, 90, "PG", ["Animation", "Action", "Comedy", "Family"], "Mark Osborne", "Kung Fu Panda", "low", "simple", ["violence"], ["funny", "exciting"], NONE),
    ("Despicable Me", 2010, 95, "PG", ["Animation", "Comedy", "Family", "Crime"], "Pierre Coffin", "Despicable Me", "low", "simple", [], ["funny", "heartwarming"], NONE),
    ("Minions", 2015, 91, "PG", ["Animation", "Comedy", "Adventure", "Family"], "Pierre Coffin", "Despicable Me", "low", "simple", [], ["funny"], NONE),
    ("Ratatouille", 2007, 111, "G", ["Animation", "Comedy", "Family", "Fantasy"], "Brad Bird", "Ratatouille", "low", "moderate", [], ["funny", "heartwarming"], NONE),
    ("WALL-E", 2008, 98, "G", ["Animation", "Science Fiction", "Family", "Romance"], "Andrew Stanton", "WALL-E", "low", "simple", [], ["calm", "heartwarming", "thoughtful"], NONE),
    ("Monsters, Inc.", 2001, 92, "G", ["Animation", "Comedy", "Family", "Fantasy"], "Pete Docter", "Monsters, Inc.", "low", "simple", ["scary_creatures"], ["funny", "heartwarming"], NONE),
    ("Cars", 2006, 117, "G", ["Animation", "Comedy", "Family", "Adventure"], "John Lasseter", "Cars", "low", "simple", [], ["funny", "heartwarming"], UNK),
    ("The Lion King", 1994, 89, "G", ["Animation", "Adventure", "Drama", "Family"], "Roger Allers", "The Lion King", "high", "simple", ["death_or_loss", "violence"], ["musical", "thoughtful"], NONE),
    ("Bambi", 1942, 70, "G", ["Animation", "Drama", "Family"], "David Hand", "Bambi", "high", "simple", ["death_or_loss"], ["calm", "thoughtful"], NONE),
    ("Dumbo", 1941, 64, "G", ["Animation", "Family", "Fantasy", "Music"], "Ben Sharpsteen", "Dumbo", "medium", "simple", ["abandonment"], ["heartwarming", "musical"], UNK),
    ("My Neighbor Totoro", 1988, 86, "G", ["Animation", "Fantasy", "Family"], "Hayao Miyazaki", "Studio Ghibli", "medium", "simple", ["serious_illness_subplot"], ["calm", "magical", "heartwarming"], NONE),
    ("Spirited Away", 2001, 125, "PG", ["Animation", "Fantasy", "Adventure", "Family"], "Hayao Miyazaki", "Studio Ghibli", "medium", "moderate", ["scary_creatures", "peril"], ["magical", "adventurous"], NONE),
    ("Ponyo", 2008, 100, "G", ["Animation", "Fantasy", "Family", "Adventure"], "Hayao Miyazaki", "Studio Ghibli", "low", "simple", [], ["calm", "magical"], NONE),
    ("Encanto", 2021, 102, "PG", ["Animation", "Comedy", "Family", "Fantasy", "Music"], "Jared Bush", "Encanto", "low", "moderate", ["family_stress"], ["musical", "magical", "heartwarming"], NONE),
    ("Luca", 2021, 95, "PG", ["Animation", "Comedy", "Family", "Fantasy", "Adventure"], "Enrico Casarosa", "Luca", "low", "simple", [], ["calm", "heartwarming", "funny"], NONE),
    ("Soul", 2020, 101, "PG", ["Animation", "Comedy", "Family", "Fantasy", "Music"], "Pete Docter", "Soul", "medium", "moderate", ["death_or_loss", "existential"], ["thoughtful", "musical"], NONE),
    ("Coraline", 2009, 100, "PG", ["Animation", "Fantasy", "Family", "Horror"], "Henry Selick", "Coraline", "high", "moderate", ["scary_creatures", "peril"], ["scary", "magical"], NONE),
    ("Paddington", 2014, 95, "PG", ["Comedy", "Family", "Adventure", "Fantasy"], "Paul King", "Paddington", "low", "simple", [], ["funny", "heartwarming"], NONE),
    ("Paddington 2", 2017, 104, "PG", ["Comedy", "Family", "Adventure", "Fantasy"], "Paul King", "Paddington", "low", "simple", [], ["funny", "heartwarming"], NONE),
    ("The Princess Bride", 1987, 99, "PG", ["Adventure", "Family", "Fantasy", "Comedy", "Romance"], "Rob Reiner", "The Princess Bride", "low", "simple", ["violence"], ["funny", "adventurous"], NONE),
    ("Home Alone", 1990, 103, "PG", ["Comedy", "Family"], "Chris Columbus", "Home Alone", "low", "simple", ["violence"], ["funny"], NONE),
    ("Matilda", 1996, 98, "PG", ["Comedy", "Family", "Fantasy"], "Danny DeVito", "Matilda", "low", "simple", ["bullying"], ["funny", "magical"], NONE),
    ("The Wizard of Oz", 1939, 102, "G", ["Adventure", "Family", "Fantasy", "Music"], "Victor Fleming", "The Wizard of Oz", "medium", "simple", ["scary_creatures", "peril"], ["musical", "magical", "adventurous"], NONE),
    ("Mary Poppins", 1964, 139, "G", ["Comedy", "Family", "Fantasy", "Music"], "Robert Stevenson", "Mary Poppins", "low", "simple", [], ["musical", "magical", "funny"], NONE),
    ("The Sound of Music", 1965, 174, "G", ["Drama", "Family", "Music", "Romance"], "Robert Wise", "The Sound of Music", "medium", "simple", ["war", "death_or_loss"], ["musical", "heartwarming"], NONE),
    ("Harry Potter and the Sorcerer's Stone", 2001, 152, "PG", ["Adventure", "Family", "Fantasy"], "Chris Columbus", "Harry Potter", "medium", "moderate", ["peril", "scary_creatures", "death_or_loss"], ["magical", "adventurous"], NONE),
    ("Wonder", 2017, 113, "PG", ["Drama", "Family"], "Stephen Chbosky", "Wonder", "medium", "simple", ["medical_care", "bullying"], ["heartwarming", "thoughtful"], NONE),
    ("March of the Penguins", 2005, 80, "G", ["Documentary", "Family"], "Luc Jacquet", "March of the Penguins", "medium", "simple", ["death_or_loss"], ["calm", "educational"], NONE),
    ("Winged Migration", 2001, 89, "G", ["Documentary", "Family"], "Jacques Perrin", "Winged Migration", "low", "simple", [], ["calm", "educational"], NONE),
    ("The Princess Diaries", 2001, 115, "G", ["Comedy", "Family", "Romance"], "Garry Marshall", "The Princess Diaries", "low", "simple", [], ["funny", "heartwarming"], NONE),
    ("Mrs. Doubtfire", 1993, 125, "PG-13", ["Comedy", "Family", "Drama"], "Chris Columbus", "Mrs. Doubtfire", "medium", "simple", ["family_stress"], ["funny", "heartwarming"], NONE),
    ("Hidden Figures", 2016, 127, "PG", ["Drama", "History"], "Theodore Melfi", "Hidden Figures", "low", "simple", ["prejudice"], ["heartwarming", "thoughtful"], NONE),
    ("The Martian", 2015, 141, "PG-13", ["Drama", "Science Fiction", "Adventure"], "Ridley Scott", "The Martian", "medium", "moderate", ["peril"], ["funny", "thoughtful", "exciting"], NONE),
    ("Apollo 13", 1995, 140, "PG", ["Drama", "History", "Adventure"], "Ron Howard", "Apollo 13", "medium", "moderate", ["peril"], ["thoughtful", "exciting"], NONE),
    ("Singin' in the Rain", 1952, 103, "G", ["Comedy", "Music", "Romance"], "Stanley Donen", "Singin' in the Rain", "low", "simple", [], ["musical", "funny"], NONE),
    ("Mamma Mia!", 2008, 108, "PG-13", ["Comedy", "Music", "Romance"], "Phyllida Lloyd", "Mamma Mia!", "low", "simple", [], ["musical", "funny", "heartwarming"], UNK),
    ("La La Land", 2016, 129, "PG-13", ["Comedy", "Drama", "Music", "Romance"], "Damien Chazelle", "La La Land", "low", "moderate", [], ["musical", "thoughtful"], UNK),
    ("Groundhog Day", 1993, 101, "PG", ["Comedy", "Fantasy", "Romance"], "Harold Ramis", "Groundhog Day", "medium", "simple", ["self_harm_reference"], ["funny", "thoughtful"], NONE),
    ("Forrest Gump", 1994, 142, "PG-13", ["Drama", "Comedy", "Romance"], "Robert Zemeckis", "Forrest Gump", "medium", "moderate", ["war", "death_or_loss", "serious_illness_subplot"], ["heartwarming", "thoughtful", "funny"], NONE),
    ("Jurassic Park", 1993, 127, "PG-13", ["Adventure", "Science Fiction", "Thriller"], "Steven Spielberg", "Jurassic Park", "high", "moderate", ["violence", "scary_creatures", "peril", "death_or_loss"], ["exciting", "scary"], UNK),
    ("Avengers: Endgame", 2019, 181, "PG-13", ["Action", "Adventure", "Science Fiction"], "Anthony Russo", "Marvel Cinematic Universe", "high", "dense", ["violence", "death_or_loss", "peril"], ["exciting"], UNK),
    ("Interstellar", 2014, 169, "PG-13", ["Science Fiction", "Drama", "Adventure"], "Christopher Nolan", "Interstellar", "medium", "dense", ["death_or_loss", "existential", "peril"], ["thoughtful"], UNK),
    ("Inception", 2010, 148, "PG-13", ["Action", "Science Fiction", "Thriller"], "Christopher Nolan", "Inception", "medium", "dense", ["violence", "peril"], ["exciting", "thoughtful"], UNK),
    ("The Lord of the Rings: The Fellowship of the Ring", 2001, 179, "PG-13", ["Adventure", "Fantasy", "Action"], "Peter Jackson", "The Lord of the Rings", "high", "dense", ["violence", "scary_creatures", "peril", "death_or_loss"], ["adventurous", "magical"], UNK),
    ("The Fault in Our Stars", 2014, 126, "PG-13", ["Drama", "Romance"], "Josh Boone", "The Fault in Our Stars", "high", "simple", ["central_serious_illness", "death_or_loss", "medical_care"], ["thoughtful"], NONE),
    ("The Shawshank Redemption", 1994, 142, "R", ["Drama", "Crime"], "Frank Darabont", "The Shawshank Redemption", "high", "moderate", ["violence"], ["thoughtful"], NONE),
    ("Chef", 2014, 114, "R", ["Comedy", "Drama"], "Jon Favreau", "Chef", "low", "simple", [], ["funny", "heartwarming"], NONE),
    ("The Conjuring", 2013, 112, "R", ["Horror", "Mystery", "Thriller"], "James Wan", "The Conjuring", "high", "moderate", ["scary_creatures", "violence", "death_or_loss"], ["scary"], UNK),
    ("Saving Private Ryan", 1998, 169, "R", ["Drama", "War", "Action"], "Steven Spielberg", "Saving Private Ryan", "high", "moderate", ["war", "violence", "visceral_gore", "death_or_loss"], ["exciting"], UNK),
]
