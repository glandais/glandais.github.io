import re
from pathlib import Path
from typing import Any

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_resume(lang: str = "fr") -> dict[str, Any]:
    path = DATA_DIR / f"resume.{lang}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return _typography(yaml.safe_load(f))


NBSP = "\u00a0"
# "17 800", "30 k€", "50 %", "12 développeurs", "22 ans"… must not break across lines
_NUMBER_GROUP = re.compile(r"(\d) (?=\d{3}\b)")
_NUMBER_UNIT = re.compile(r"(\d) (?=(?:%|k€|€|ans?\b|mois\b|semaines?\b|jours?\b|j/h\b|req/s\b|développeurs\b|personnes\b|commits\b|pages\b))")


def _typography(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _typography(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_typography(v) for v in value]
    if isinstance(value, str):
        value = _NUMBER_GROUP.sub(rf"\1{NBSP}", value)
        return _NUMBER_UNIT.sub(rf"\1{NBSP}", value)
    return value


def get_full_name(data: dict) -> str:
    return data["basics"]["name"]


def get_filename_base(data: dict) -> str:
    """Return 'Prenom_Nom_CV_LANG' for generated file names."""
    name = get_full_name(data)
    parts = name.split()
    lang = data["meta"]["lang"].upper()
    return f"{'_'.join(parts)}_CV_{lang}"


def normalize_text(text: str) -> str:
    """Collapse line breaks and repeated spaces (e.g. YAML literal blocks)."""
    return " ".join(text.split())
