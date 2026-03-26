import re

def extract_id(text: str):
    match = re.search(r"\b([A-Z]?\d{5,})\b", text)
    if match:
        return match.group(1)
    return None