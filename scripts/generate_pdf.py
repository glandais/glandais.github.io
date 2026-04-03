# scripts/generate_pdf.py
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from scripts.resume_loader import get_filename_base

DIST_DIR = Path(__file__).resolve().parent.parent / "dist"
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def generate_pdf(data: dict) -> Path:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR / "ats")))
    template = env.get_template("resume.html.j2")
    html_str = template.render(data=data)

    out_dir = DIST_DIR / "pdf"
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = get_filename_base(data) + ".pdf"
    out_path = out_dir / filename

    HTML(string=html_str).write_pdf(str(out_path))
    return out_path
