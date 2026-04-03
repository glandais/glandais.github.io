# tests/test_generate_pdf.py
from pathlib import Path
from scripts.resume_loader import load_resume
from scripts.generate_pdf import generate_pdf


def test_generate_pdf_creates_file(tmp_path, monkeypatch):
    import scripts.generate_pdf as mod
    monkeypatch.setattr(mod, "DIST_DIR", tmp_path)
    data = load_resume("fr")
    out = generate_pdf(data)
    assert out.exists()
    assert out.suffix == ".pdf"
    assert out.stat().st_size > 1000
