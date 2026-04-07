import re

def extract_experience(text):

    text = text.lower()

    # detect patterns like "3 years", "5 yrs"
    matches = re.findall(r'(\d+)\s*(year|years|yr|yrs)', text)

    if matches:
        years = max(int(m[0]) for m in matches)
        return f"Experienced ({years} years)"

    return "Fresher"