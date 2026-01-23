import re 


def clean_name(name: str) -> str:
    name = re.sub(r"[^а-яА-Яa-zA-Z0-9\s]", "", name)
    return re.sub(r"\s+", " ", name).strip()
