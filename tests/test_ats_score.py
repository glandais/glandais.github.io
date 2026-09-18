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
