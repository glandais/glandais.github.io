from pathlib import Path
from scripts.resume_loader import load_resume


def test_load_resume_fr():
    data = load_resume("fr")
    assert data["basics"]["name"] == "Gabriel Landais"
    assert data["meta"]["lang"] == "fr"
    assert len(data["experience"]) > 0
    assert len(data["skills"]) > 0


def test_load_resume_returns_all_sections():
    data = load_resume("fr")
    for key in ["meta", "basics", "skills", "experience", "education", "projects", "languages"]:
        assert key in data, f"Missing section: {key}"


def test_load_resume_missing_lang_raises():
    import pytest
    with pytest.raises(FileNotFoundError):
        load_resume("zz")
