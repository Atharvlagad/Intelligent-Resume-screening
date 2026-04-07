from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

import tempfile
import os
import zipfile
import pandas as pd

from parser.pdf_parser import extract_text_from_pdf
from extractor.text_cleaner import clean_text
from extractor.info_extractor import extract_email, extract_phone, extract_name
from extractor.skills_extractor import extract_skills, match_skills
from extractor.jd_extractor import extract_skills_from_jd
from extractor.experience_extractor import extract_experience
from extractor.similarity_extractor import compute_similarity


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def load_ui():
    with open("frontend/index.html") as f:
        return f.read()


def process_resumes(zip_file, job_description, min_score):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
        temp_zip.write(zip_file)
        zip_path = temp_zip.name

    extract_folder = tempfile.mkdtemp()

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

    os.remove(zip_path)

    hr_required_skills = extract_skills_from_jd(job_description)

    results = []

    for file_name in os.listdir(extract_folder):

        if not file_name.lower().endswith(".pdf"):
            continue

        file_path = os.path.join(extract_folder, file_name)

        text = extract_text_from_pdf(file_path)

        if not text:
            continue

        name = extract_name(text)
        email = extract_email(text)
        phone = extract_phone(text)
        experience = extract_experience(text)

        cleaned_text = clean_text(text)
        candidate_skills = extract_skills(cleaned_text)

        skill_match = match_skills(candidate_skills, hr_required_skills)

        ai_similarity = compute_similarity(text, job_description)

        results.append({
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Experience": experience,
            "Matching Skills": ", ".join(skill_match["matched_skills"]),
            "Missing Skills": ", ".join(skill_match["missing_skills"]),
            "Skill Score": skill_match["score"],
            "AI Match": ai_similarity
        })

    results = sorted(results, key=lambda x: x["Skill Score"], reverse=True)

    for i, r in enumerate(results, start=1):
        r["Rank"] = i

    # FILTER BY MIN SCORE
    results = [r for r in results if r["Skill Score"] >= min_score]

    return results


@app.post("/rank-resumes")
async def rank_resumes(
    zip_file: UploadFile = File(...),
    job_description: str = Form(...),
    min_score: int = Form(...)
):

    zip_bytes = await zip_file.read()

    results = process_resumes(zip_bytes, job_description, min_score)

    return results


@app.post("/rank-resumes/download")
async def rank_resumes_download(
    zip_file: UploadFile = File(...),
    job_description: str = Form(...),
    min_score: int = Form(...)
):

    zip_bytes = await zip_file.read()

    results = process_resumes(zip_bytes, job_description, min_score)

    df = pd.DataFrame(results)

    output_file = "ranked_resumes.xlsx"
    df.to_excel(output_file, index=False)

    return FileResponse(
        path=output_file,
        filename="ranked_resumes.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )