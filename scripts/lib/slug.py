import re


def slugify(text: str, max_length: int = 60) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower().strip())
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:max_length].strip("-")
