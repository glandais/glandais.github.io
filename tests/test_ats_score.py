from scripts.ats_score import extract_resume_keywords, compute_score


def test_extract_resume_keywords():
    data = {
        "skills": [{"category": "Backend", "keywords": ["Java", "Python"]}],
        "experience": [
            {"highlights": ["Developed Java services"], "keywords_ats": ["Spring Boot"], "stack": "Java, Docker"}
        ],
    }
    kws = extract_resume_keywords(data)
    assert "java" in kws
    assert "python" in kws
    assert "spring boot" in kws
    assert "docker" in kws


def test_extract_resume_keywords_includes_early_career():
    data = {"early_career": [{"period": "2007 – 2008", "company": "X", "summary": "s", "stack": "Tapestry, EJB3"}]}
    kws = extract_resume_keywords(data)
    assert "tapestry" in kws
    assert "ejb3" in kws


def test_compute_score_full_match():
    resume_kws = {"java", "python", "docker"}
    job_text = "We need Java and Python and Docker experience"
    result = compute_score(resume_kws, job_text)
    assert result["score"] == 100.0
    assert len(result["missing"]) == 0


def test_compute_score_partial_match():
    resume_kws = {"java", "python"}
    job_text = "We need Java, Python, Kubernetes, and Terraform"
    result = compute_score(resume_kws, job_text)
    assert result["score"] > 0
    assert "kubernetes" in result["missing"]
    assert "terraform" in result["missing"]
    assert "java" in result["found"]


def test_compute_score_empty_job():
    resume_kws = {"java"}
    result = compute_score(resume_kws, "")
    assert result["score"] == 0.0


def test_keyword_matching_uses_word_boundaries():
    # "go" must not match inside "catégorie", "vue" not inside "revue"
    result = compute_score(set(), "Go et Vue", full_text="une catégorie en revue")
    assert "go" in result["missing"]
    assert "vue" in result["missing"]


def test_composite_skill_labels_are_split():
    data = {"skills": [{"category": "Méthodes", "keywords": ["Agile (Scrum, SAFe)", "OAuth2 / OIDC"]}]}
    kws = extract_resume_keywords(data)
    assert {"scrum", "safe", "oauth2", "oidc"} <= kws


def test_full_text_counts_highlights():
    from scripts.ats_score import resume_text
    data = {"experience": [{"title": "Architecte", "company": "X", "highlights": ["Mise en place de Kubernetes"]}]}
    result = compute_score(set(), "Kubernetes requis", full_text=resume_text(data))
    assert "kubernetes" in result["found"]


def test_common_capitalized_words_are_ignored():
    result = compute_score(set(), "Missions : Concevoir des API. Profil : Java")
    assert "missions" not in result["job_keywords"]
    assert "profil" not in result["job_keywords"]
