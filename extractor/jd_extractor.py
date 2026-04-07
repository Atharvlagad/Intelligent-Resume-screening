from rake_nltk import Rake
import re

# words that should never be treated as skills
IGNORE_WORDS = {
    "looking",
    "experience",
    "developer",
    "strong",
    "skills",
    "good",
    "knowledge",
    "required",
    "ability",
    "candidate",
    "team",
    "work",
    "role",
    "position"
}


def extract_skills_from_jd(job_description):

    r = Rake()

    r.extract_keywords_from_text(job_description)

    keywords = r.get_ranked_phrases()

    skills = []

    for kw in keywords:

        kw = kw.lower().strip()

        # remove numbers/symbols
        kw = re.sub(r"[^a-zA-Z\s]", "", kw)

        # ignore short words
        if len(kw) < 3:
            continue

        # ignore unwanted keywords
        if kw in IGNORE_WORDS:
            continue

        # ignore phrases longer than 3 words
        if len(kw.split()) > 3:
            continue

        skills.append(kw)

    # remove duplicates
    skills = list(set(skills))

    print("JD Extracted Skills:", skills)

    return skills