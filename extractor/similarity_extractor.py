from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_similarity(resume_text, job_description):

    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    jd_embedding = model.encode(job_description, convert_to_tensor=True)

    similarity = util.cos_sim(resume_embedding, jd_embedding)

    score = float(similarity[0][0]) * 100

    return round(score, 2)