import re

def clean_text(text):
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters (keep letters, numbers, basic punctuation)
    text = re.sub(r'[^a-zA-Z0-9@.+\-\s]', '', text)

    return text.strip()