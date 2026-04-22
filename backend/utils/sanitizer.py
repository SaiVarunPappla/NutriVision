import re

def sanitize_ingredient(ingredient: str) -> str:
    # 1. Remove everything inside parentheses
    clean = re.sub(r'\s*\([^)]*\)', '', ingredient)
    # 2. Remove common punctuation at end
    clean = re.sub(r'[),]+$', '', clean)
    # 3. Normalize whitespace
    clean = ' '.join(clean.split())
    return clean.strip()
