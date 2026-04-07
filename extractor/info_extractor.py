import re


# -----------------------------------------
# EMAIL EXTRACTION (GLOBAL)
# -----------------------------------------
def extract_email(text):

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)

    return match.group() if match else "NOT AVAILABLE"


# -----------------------------------------
# PHONE EXTRACTION (GLOBAL)
# -----------------------------------------
# -----------------------------------------
# PHONE EXTRACTION (ROBUST VERSION)
# -----------------------------------------
def extract_phone(text):

    # Normalize weird dash characters
    text = text.replace("‐", "-").replace("–", "-").replace("—", "-")

    # Find all possible phone-like patterns
    phone_candidates = re.findall(r'[\+()0-9\s\-]{8,20}', text)

    for candidate in phone_candidates:

        digits = re.sub(r'\D', '', candidate)

        # Valid phone numbers usually between 10–13 digits
        if 10 <= len(digits) <= 13:
            return candidate.strip()

    return "NOT AVAILABLE"


# -----------------------------------------
# NAME EXTRACTION (STABLE VERSION)
# -----------------------------------------
def extract_name(text):

    lines = text.split("\n")
    email = extract_email(text)

    section_titles = [
        "career", "objective", "summary", "profile",
        "education", "skills", "technical",
        "projects", "experience", "certifications",
        "languages", "interests"
    ]

    # ---------------------------------
    # STRATEGY 1: Email-anchored detection
    # ---------------------------------
    if email != "NOT AVAILABLE":

        for i, line in enumerate(lines):

            if email in line:

                # Check previous 2 lines for name
                for j in range(max(0, i - 2), i):

                    candidate = lines[j].strip()

                    if not candidate:
                        continue

                    if any(char.isdigit() for char in candidate):
                        continue

                    lower_candidate = candidate.lower()
                    if any(title in lower_candidate for title in section_titles):
                        continue

                    cleaned = re.sub(r'[^a-zA-Z\s.]', '', candidate)

                    # Handle joined CamelCase names (HaydenSmith)
                    if cleaned.isalpha() and cleaned != cleaned.lower():
                        split_name = re.findall(r'[A-Z][a-z]+', cleaned)
                        if 1 < len(split_name) <= 3:
                            return " ".join(split_name)

                    words = cleaned.replace(".", "").split()

                    if 1 < len(words) <= 3 and all(word.isalpha() for word in words):
                        return " ".join(words)

                break

    # ---------------------------------
    # STRATEGY 2: Top 5 lines fallback
    # ---------------------------------
    for line in lines[:5]:

        candidate = line.strip()

        if not candidate:
            continue

        if any(char.isdigit() for char in candidate):
            continue

        lower_candidate = candidate.lower()
        if any(title in lower_candidate for title in section_titles):
            continue

        cleaned = re.sub(r'[^a-zA-Z\s.]', '', candidate)

        # Handle joined names
        if cleaned.isalpha() and cleaned != cleaned.lower():
            split_name = re.findall(r'[A-Z][a-z]+', cleaned)
            if 1 < len(split_name) <= 3:
                return " ".join(split_name)

        words = cleaned.replace(".", "").split()

        if 1 < len(words) <= 3 and all(word.isalpha() for word in words):
            return " ".join(words)

    return "NOT AVAILABLE"