import os
import pandas as pd

from parser.pdf_parser import extract_text_from_pdf
from extractor.text_cleaner import clean_text
from extractor.info_extractor import extract_email, extract_phone, extract_name
from extractor.skills_extractor import extract_skills, match_skills


# ----------------------------------------
# HR REQUIRED SKILLS
# ----------------------------------------
hr_required_skills = ["python", "sql", "machine learning", "excel"]


# ----------------------------------------
# PATH SETUP
# ----------------------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(base_dir, "data")
output_folder = os.path.join(base_dir, "output")

os.makedirs(output_folder, exist_ok=True)

results = []


# ----------------------------------------
# PROCESS ALL PDF FILES
# ----------------------------------------
for file_name in os.listdir(data_folder):

    if file_name.endswith(".pdf"):

        file_path = os.path.join(data_folder, file_name)
        print("\nProcessing:", file_name)

        text = extract_text_from_pdf(file_path)

        if not text:
            continue

        # Use RAW text for header extraction
        name = extract_name(text)
        email = extract_email(text)
        phone = extract_phone(text)

        # Use cleaned text for skills
        cleaned_text = clean_text(text)
        candidate_skills = extract_skills(cleaned_text)
        result = match_skills(candidate_skills, hr_required_skills)

        display_name = name if name != "NOT AVAILABLE" else file_name

        resume_data = {
            "file_name": file_name,
            "name": display_name,
            "email": email,
            "phone": phone,
            "matched_skills": ", ".join(result["matched_skills"]),
            "missing_skills": ", ".join(result["missing_skills"]),
            "score": result["score"]
        }

        results.append(resume_data)


# ----------------------------------------
# SORT BY SCORE
# ----------------------------------------
ranked_results = sorted(results, key=lambda x: x["score"], reverse=True)

print("\n========== FINAL RANKING ==========\n")

for rank, resume in enumerate(ranked_results, start=1):
    print(f"Rank {rank}: {resume['name']} - Score: {resume['score']}%")


# ----------------------------------------
# EXPORT TO EXCEL
# ----------------------------------------
excel_path = os.path.join(output_folder, "ranked_resumes.xlsx")

df = pd.DataFrame(ranked_results)
df.to_excel(excel_path, index=False)

print("\nExcel file generated at:")
print(excel_path)
