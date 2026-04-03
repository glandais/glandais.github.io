# CV-as-Code

## Quick start
uv sync
uv run python -m scripts.build all --lang fr

## Test
uv run pytest

## Architecture
- Single YAML source in `data/resume.{lang}.yaml`
- Generators in `scripts/generate_*.py` each produce one format
- CLI entry point: `scripts/build.py` (Typer)
- ATS constraints: no tables, no columns, no headers/footers in DOCX, Calibri font, single-column layout

## Conventions
- Python 3.11+, type hints
- Templates in `templates/` (Jinja2)
- Build output to `dist/` (gitignored), site to `docs/` (committed)
