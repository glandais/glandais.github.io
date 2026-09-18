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


# Capitalized words that are ordinary French/English vocabulary, not skills
STOPWORDS = {
    "missions", "mission", "profil", "profile", "poste", "contexte", "description", "compétences",
    "expérience", "expériences", "vous", "nous", "notre", "nos", "votre", "les", "des", "une", "dans",
    "pour", "avec", "sur", "par", "the", "and", "you", "our", "your", "with", "concevoir", "participer",
    "maîtrise", "connaissance", "connaissances", "environnement", "rattaché", "rattachée", "au", "sein",
    "entreprise", "société", "client", "clients", "équipe", "équipes", "idéalement", "une", "freelance",
    "cdi", "cdd", "remote", "télétravail", "nantes", "paris", "france", "lieu", "durée", "démarrage",
    "tjm", "salaire", "avantages", "bonus", "atouts", "atout", "qualités", "savoir", "être", "ans",
    "vos", "accompagner", "contribuer", "industrialiser", "porter", "encadrer", "garantir", "mettre",
    "optimiser", "cadrer", "positionner", "travailler", "piloter", "définir", "assurer", "animer",
}

_SPLIT_RE = re.compile(r"\s*[/,;()]\s*")


def _keyword_variants(label: str) -> set[str]:
    """'Agile (Scrum, SAFe)' -> {'agile (scrum, safe)', 'agile', 'scrum', 'safe'}."""
    label = label.strip().lower()
    variants = {label}
    variants.update(part.strip() for part in _SPLIT_RE.split(label) if len(part.strip()) > 1)
    return variants


def resume_text(data: dict) -> str:
    """Everything a parser would read from the rendered CV (lowercased)."""
    parts: list[str] = []
    basics = data.get("basics", {})
    parts += [basics.get("label", ""), basics.get("summary", "")]
    for group in data.get("skills", []):
        parts.append(group.get("category", ""))
        parts += group.get("keywords", [])
    for exp in data.get("experience", []):
        parts += [exp.get("title", ""), exp.get("company", ""), exp.get("stack", "")]
        parts += exp.get("highlights", [])
    for item in data.get("early_career", []):
        parts += [item.get("company", ""), item.get("title", ""), item.get("summary", ""), item.get("stack", "")]
    for proj in data.get("projects", []):
        parts += [proj.get("name", ""), proj.get("description", "")]
        parts += proj.get("keywords", [])
    for edu in data.get("education", []):
        parts += [edu.get("studyType", ""), edu.get("area", ""), edu.get("institution", "")]
    return " ".join(p for p in parts if p).lower()


def extract_resume_keywords(data: dict) -> set[str]:
    kws: set[str] = set()
    for group in data.get("skills", []):
        for kw in group.get("keywords", []):
            kws |= _keyword_variants(kw)

    for exp in data.get("experience", []):
        for kw in exp.get("keywords_ats", []):
            kws |= _keyword_variants(kw)
        if exp.get("stack"):
            for part in exp["stack"].split(","):
                kws |= _keyword_variants(part)

    for item in data.get("early_career", []):
        if item.get("stack"):
            for part in item["stack"].split(","):
                kws |= _keyword_variants(part)

    for proj in data.get("projects", []):
        for kw in proj.get("keywords", []):
            kws |= _keyword_variants(kw)

    return kws


def _contains(text: str, kw: str) -> bool:
    """Whole-word match, tolerant of symbols such as 'c++' or 'ci/cd'."""
    return re.search(rf"(?<![\w]){re.escape(kw)}(?![\w])", text) is not None


def _extract_job_keywords(job_text: str) -> set[str]:
    text_lower = job_text.lower()
    found = {kw for kw in TECH_KEYWORDS if _contains(text_lower, kw)}
    words = re.findall(r"\b[A-Z][a-zA-Z0-9+#.]{2,}\b", job_text)
    for w in words:
        w = w.lower().rstrip(".")
        if w not in STOPWORDS:
            found.add(w)
    return found


def compute_score(resume_keywords: set[str], job_text: str, full_text: str = "") -> dict:
    job_kws = _extract_job_keywords(job_text)
    if not job_kws:
        return {"score": 0.0, "found": set(), "missing": set(), "job_keywords": set()}

    found = {kw for kw in job_kws if kw in resume_keywords or (full_text and _contains(full_text, kw))}
    missing = job_kws - found
    score = (len(found) / len(job_kws)) * 100

    return {
        "score": round(score, 1),
        "found": found,
        "missing": missing,
        "job_keywords": job_kws,
    }


def score_ats(data: dict, job_path: Path):
    job_text = job_path.read_text(encoding="utf-8")
    resume_kws = extract_resume_keywords(data)
    result = compute_score(resume_kws, job_text, resume_text(data))

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
