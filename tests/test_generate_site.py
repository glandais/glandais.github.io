from pathlib import Path
from scripts.resume_loader import load_resume
from scripts.generate_site import generate_site


def test_generate_site_creates_index(tmp_path, monkeypatch):
    import scripts.generate_site as mod
    monkeypatch.setattr(mod, "DOCS_DIR", tmp_path)
    data = load_resume("fr")
    out = generate_site(data)
    index = tmp_path / "index.html"
    assert index.exists()
    content = index.read_text()
    assert "Gabriel Landais" in content


def test_generate_site_copies_css(tmp_path, monkeypatch):
    import scripts.generate_site as mod
    monkeypatch.setattr(mod, "DOCS_DIR", tmp_path)
    data = load_resume("fr")
    generate_site(data)
    assert (tmp_path / "style.css").exists()
