# extractor/skills_extractor.py

import re
from sentence_transformers import SentenceTransformer, util

# ----------------------------------------
# AI MODEL
# ----------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

# ----------------------------------------
# MASTER SKILL LIST
# ----------------------------------------

MASTER_SKILLS = [
    "python", "java", "c++", "c", "sql", "mysql",
    "machine learning", "deep learning",
    "excel", "power bi", "tableau",
    "communication", "leadership",
    "html", "css", "javascript",
    "react", "node", "django", "flask",
    "data analysis", "pandas", "numpy"
]
# Precompute embeddings
MASTER_EMBEDDINGS = model.encode(MASTER_SKILLS)


# ----------------------------------------
# EXTRACT SKILLS FROM RESUME
# ----------------------------------------

def extract_skills(text):

    text = text.lower()
    words = re.findall(r"[a-zA-Z+#]+", text)

    found_skills = set()

    for word in words:

        word_embedding = model.encode(word)

        similarities = util.cos_sim(word_embedding, MASTER_EMBEDDINGS)

        best_match_index = similarities.argmax()
        score = similarities[0][best_match_index]

        if score > 0.6:   # similarity threshold
            found_skills.add(MASTER_SKILLS[best_match_index])

    return list(found_skills)


# ----------------------------------------
# MATCH HR SKILLS
# ----------------------------------------

def match_skills(candidate_skills, hr_required_skills):

    matched = []
    missing = []

    for skill in hr_required_skills:

        skill_embedding = model.encode(skill)

        best_score = 0

        for candidate_skill in candidate_skills:

            candidate_embedding = model.encode(candidate_skill)

            score = util.cos_sim(skill_embedding, candidate_embedding)

            best_score = max(best_score, score.item())

        if best_score > 0.6:
            matched.append(skill)
        else:
            missing.append(skill)

    score = 0

    if hr_required_skills:
        score = round((len(matched) / len(hr_required_skills)) * 100, 2)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "score": score
    }