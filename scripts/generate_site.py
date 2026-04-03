# scripts/generate_site.py
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scripts.resume_loader import get_filename_base

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def generate_site(data: dict) -> Path:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR / "visual")))
    template = env.get_template("resume.html.j2")
    filename_base = get_filename_base(data)
    html = template.render(data=data, filename_base=filename_base)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")

    css_src = TEMPLATES_DIR / "visual" / "style.css"
    shutil.copy2(css_src, DOCS_DIR / "style.css")

    return DOCS_DIR
