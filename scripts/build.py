# scripts/build.py
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint

app = typer.Typer(help="CV-as-Code: generate resumes from YAML source")

DIST_DIR = Path(__file__).resolve().parent.parent / "dist"


@app.command()
def all(lang: Annotated[str, typer.Option(help="Language code")] = "fr"):
    """Generate all formats (DOCX, PDF, site)."""
    docx(lang=lang)
    pdf(lang=lang)
    site(lang=lang)
    rprint(f"[green]All formats generated for lang={lang}[/green]")


@app.command()
def docx(lang: Annotated[str, typer.Option(help="Language code")] = "fr"):
    """Generate ATS-friendly DOCX."""
    from scripts.generate_docx import generate_docx
    from scripts.resume_loader import load_resume

    data = load_resume(lang)
    out = generate_docx(data)
    rprint(f"[green]DOCX generated: {out}[/green]")


@app.command()
def pdf(lang: Annotated[str, typer.Option(help="Language code")] = "fr"):
    """Generate PDF via WeasyPrint."""
    from scripts.generate_pdf import generate_pdf
    from scripts.resume_loader import load_resume

    data = load_resume(lang)
    out = generate_pdf(data)
    rprint(f"[green]PDF generated: {out}[/green]")


@app.command()
def site(lang: Annotated[str, typer.Option(help="Language code")] = "fr"):
    """Generate static site for GitHub Pages."""
    from scripts.generate_site import generate_site
    from scripts.resume_loader import load_resume

    data = load_resume(lang)
    out = generate_site(data)
    rprint(f"[green]Site generated: {out}[/green]")


@app.command()
def ats_score(
    job: Annotated[Path, typer.Option(help="Path to job description text file")],
    lang: Annotated[str, typer.Option(help="Language code")] = "fr",
):
    """Score resume keywords against a job description."""
    from scripts.ats_score import score_ats
    from scripts.resume_loader import load_resume

    data = load_resume(lang)
    score_ats(data, job)


@app.command()
def linkedin_diff(
    export: Annotated[Path, typer.Option(help="Path to LinkedIn CSV export")],
    lang: Annotated[str, typer.Option(help="Language code")] = "fr",
):
    """Diff YAML source vs LinkedIn CSV export."""
    from scripts.linkedin_diff import diff_linkedin
    from scripts.resume_loader import load_resume

    data = load_resume(lang)
    diff_linkedin(data, export)


if __name__ == "__main__":
    app()
