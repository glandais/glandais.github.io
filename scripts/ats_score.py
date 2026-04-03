import re
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

TECH_KEYWORDS = {
    "java", "python", "javascript", "typescript", "go", "rust", "c++", "c#",
    "spring boot", "spring", "quarkus", "django", "flask", "fastapi", "express",
    "react", "vue", "vue 3", "angular", "svelte",
    "docker", "kubernetes", "helm", "terraform", "ansible",
    "aws", "gcp", "azure", "google cloud",
    "postgresql", "mysql", "mongodb", "cassandra", "elasticsearch", "redis", "sqlite",
    "kafka", "rabbitmq", "pulsar",
    "rest", "graphql", "grpc",
    "ci/cd", "github actions", "jenkins", "gitlab ci",
    "agile", "scrum", "tdd",
    "microservices", "api", "oauth2", "jwt",
    "prometheus", "grafana", "elk",
    "jpa", "hibernate",
}


def extract_resume_keywords(data: dict) -> set[str]:
    kws = set()
    for group in data.get("skills", []):
        for kw in group.get("keywords", []):
            kws.add(kw.lower())

    for exp in data.get("experience", []):
        for kw in exp.get("keywords_ats", []):
            kws.add(kw.lower())
        if exp.get("stack"):
            for part in exp["stack"].split(","):
                kws.add(part.strip().lower())

    for proj in data.get("projects", []):
        for kw in proj.get("keywords", []):
            kws.add(kw.lower())

    return kws


def _extract_job_keywords(job_text: str) -> set[str]:
    text_lower = job_text.lower()
    found = set()
    for kw in TECH_KEYWORDS:
        if kw in text_lower:
            found.add(kw)
    words = re.findall(r"\b[A-Z][a-zA-Z0-9+#.]{2,}\b", job_text)
    for w in words:
        found.add(w.lower())
    return found


def compute_score(resume_keywords: set[str], job_text: str) -> dict:
    job_kws = _extract_job_keywords(job_text)
    if not job_kws:
        return {"score": 0.0, "found": set(), "missing": set(), "job_keywords": set()}

    found = resume_keywords & job_kws
    missing = job_kws - resume_keywords
    score = (len(found) / len(job_kws)) * 100 if job_kws else 0

    return {
        "score": round(score, 1),
        "found": found,
        "missing": missing,
        "job_keywords": job_kws,
    }


def score_ats(data: dict, job_path: Path):
    job_text = job_path.read_text(encoding="utf-8")
    resume_kws = extract_resume_keywords(data)
    result = compute_score(resume_kws, job_text)

    console.print(f"\n[bold]Score ATS : {result['score']:.1f}%[/bold]")
    if result["score"] >= 80:
        console.print("[green]Excellent — score cible atteint[/green]")
    elif result["score"] >= 60:
        console.print("[yellow]Correct — quelques mots-clés manquants[/yellow]")
    else:
        console.print("[red]Insuffisant — mots-clés critiques manquants[/red]")

    table = Table(title="Mots-clés trouvés")
    table.add_column("Mot-clé", style="green")
    for kw in sorted(result["found"]):
        table.add_row(kw)
    console.print(table)

    if result["missing"]:
        table = Table(title="Mots-clés manquants")
        table.add_column("Mot-clé", style="red")
        for kw in sorted(result["missing"]):
            table.add_row(kw)
        console.print(table)

        console.print("\n[bold]Suggestions :[/bold]")
        console.print("Ajoutez les mots-clés manquants dans les sections appropriées du YAML source.")
