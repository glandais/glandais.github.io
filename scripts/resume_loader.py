from pathlib import Path
from typing import Any

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_resume(lang: str = "fr") -> dict[str, Any]:
    path = DATA_DIR / f"resume.{lang}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_full_name(data: dict) -> str:
    return data["basics"]["name"]


def get_filename_base(data: dict) -> str:
    """Return 'Prenom_Nom_CV_LANG' for generated file names."""
    name = get_full_name(data)
    parts = name.split()
    lang = data["meta"]["lang"].upper()
    return f"{'_'.join(parts)}_CV_{lang}"
