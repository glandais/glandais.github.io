# CV-as-Code — ATS Resume Pipeline

## Vue d'ensemble du projet

Projet de gestion de CV versionné sous Git, avec un format source YAML (pivot)
qui génère automatiquement :
- **DOCX** (ATS-friendly, compatible Word)
- **PDF** (via WeasyPrint)
- **Site statique** hébergé sur GitHub Pages

La philosophie est : **une seule source de vérité**, plusieurs rendus.

---

## Stack technique

- **Format pivot** : YAML (inspiré du standard JSON Resume)
- **Génération DOCX** : `python-docx`
- **Génération PDF** : WeasyPrint (HTML → PDF, pas de dépendance LaTeX)
- **Génération site** : Jinja2 → HTML statique
- **ATS scoring** : analyse de mots-clés vs offres d'emploi (CLI)
- **LinkedIn** : script de diff entre le YAML source et un export LinkedIn CSV
- **CI/CD** : GitHub Actions (build + deploy GitHub Pages)
- **Langue** : Python 3.11+

---

## Structure du projet à initialiser

```
cv-as-code/
├── CLAUDE.md
├── README.md
├── pyproject.toml           # deps: python-docx, weasyprint, jinja2, pyyaml, typer
├── data/
│   ├── resume.fr.yaml       # Version française (source principale)
│   └── resume.en.yaml       # Version anglaise
├── templates/
│   ├── ats/
│   │   └── resume.html.j2   # Template HTML ATS-friendly (single column)
│   └── visual/
│       └── resume.html.j2   # Template HTML visuel pour le site
├── scripts/
│   ├── build.py             # Entry point CLI principal (typer)
│   ├── generate_docx.py     # DOCX via python-docx
│   ├── generate_pdf.py      # PDF via WeasyPrint
│   ├── generate_site.py     # Site statique via Jinja2
│   ├── ats_score.py         # Scoring ATS vs une offre d'emploi
│   └── linkedin_diff.py     # Diff YAML source vs export LinkedIn CSV
├── dist/                    # Gitignored, généré localement
│   ├── docx/
│   ├── pdf/
│   └── site/
├── docs/                    # Dossier GitHub Pages (committé)
│   └── (généré par scripts/generate_site.py)
└── .github/
    └── workflows/
        └── build.yml        # CI : build + deploy pages sur push main
```

---

## Schéma YAML pivot

Le fichier `data/resume.fr.yaml` doit suivre ce schéma :

```yaml
meta:
  version: "1.0"
  updated: "2025-01"
  lang: "fr"

basics:
  name: "Prénom Nom"
  label: "Développeur Full-Stack Java / Vue 3"
  email: "prenom.nom@email.com"
  phone: "+33 6 XX XX XX XX"
  location:
    city: "Nantes"
    region: "Pays de la Loire"
    country: "France"
  linkedin: "linkedin.com/in/monprofil"
  github: "github.com/monpseudo"
  website: "monsite.fr"
  summary: |
    Développeur freelance spécialisé Java/Quarkus et Vue 3...

skills:
  - category: "Backend"
    keywords: ["Java", "Quarkus", "Spring Boot", "Python", "REST", "JPA"]
  - category: "Frontend"
    keywords: ["Vue 3", "React", "TypeScript", "Vite"]
  - category: "DevOps & Infra"
    keywords: ["Docker", "Kubernetes", "GitHub Actions", "PostgreSQL"]

experience:
  - title: "Développeur Freelance"
    company: "Micro-entreprise"
    startDate: "2022-01"
    endDate: null   # null = poste actuel
    location: "Nantes (remote)"
    highlights:
      - "Conception et développement de Tribly, plateforme multi-tenant pour clubs cyclistes"
      - "Développement de Pedalons.fr, plateforme de gestion de sorties cyclistes"
    keywords_ats: ["Quarkus", "Vue 3", "multi-tenant", "Keycloak", "PostgreSQL"]

education:
  - institution: "Nom de l'école"
    area: "Informatique"
    studyType: "Master / Licence / BTS"
    startDate: "20XX"
    endDate: "20XX"

projects:
  - name: "Tribly"
    url: "https://tribly.fr"
    description: "Plateforme SaaS multi-tenant pour la gestion de clubs cyclistes"
    keywords: ["Quarkus", "Vue 3", "PostgreSQL", "Keycloak"]
  - name: "Pedalons"
    url: "https://pedalons.fr"
    description: "Plateforme communautaire de sorties et routes cyclistes"
    keywords: ["MapLibre", "GPX", "PMTiles", "Rust"]

languages:
  - language: "Français"
    fluency: "Langue maternelle"
  - language: "Anglais"
    fluency: "Professionnel"

certifications: []
```

---

## Tâches d'initialisation (à faire dans l'ordre)

### 1. Bootstrap du projet Python

Créer la structure de fichiers ci-dessus et initialiser `pyproject.toml`.

Dépendances : `python-docx`, `weasyprint`, `jinja2`, `pyyaml`, `typer`, `rich`

### 2. Implémenter `scripts/build.py` (CLI Typer)

Commandes à exposer :

```
python scripts/build.py all [--lang fr|en]
python scripts/build.py docx [--lang fr|en]
python scripts/build.py pdf [--lang fr|en]
python scripts/build.py site [--lang fr|en]
python scripts/build.py ats-score --job job.txt
python scripts/build.py linkedin-diff --export linkedin_export.csv
```

### 3. Implémenter `scripts/generate_docx.py`

Règles ATS strictes (ref: https://skills.sh/paramchoudhary/resumeskills/resume-ats-optimizer) :

- Police standard : Calibri 11pt corps, 14pt nom, 12pt titres sections
- **Pas de tableau, pas de colonne, pas d'en-tête/pied de page Word**
- Informations de contact dans le corps du document
- Titres de sections : "Expérience professionnelle", "Formation", "Compétences", "Projets"
- Puces standard (•)
- Marges : 2cm tous côtés
- Nom de fichier généré : `Prenom_Nom_CV_FR.docx`

### 4. Implémenter `scripts/generate_pdf.py`

- Utiliser WeasyPrint (pas de dépendance LaTeX)
- Basé sur le template HTML ATS (`templates/ats/resume.html.j2`)
- Résultat : `Prenom_Nom_CV_FR.pdf`

### 5. Implémenter `scripts/generate_site.py`

- Template visuel distinct du template ATS
- Générer dans `docs/` (pour GitHub Pages)
- Support bilingue FR/EN avec switcher de langue
- Design propre et lisible (single page)
- Inclure liens vers téléchargement PDF et DOCX

### 6. Implémenter `scripts/ats_score.py`

Prend en argument un fichier texte d'offre d'emploi et calcule :

- Score de correspondance (keywords du YAML vs offre)
- Keywords manquants critiques
- Keywords présents
- Suggestions d'ajout dans les sections

Score cible : 80%+

### 7. Implémenter `scripts/linkedin_diff.py`

- Accepter l'export CSV de LinkedIn (Settings > Data Privacy > Get a copy)
- Comparer les champs clés (poste actuel, entreprise, dates, compétences)
- Afficher un diff coloré des champs désynchronisés
- Générer un rapport Markdown `linkedin_diff_report.md`

### 8. GitHub Actions `.github/workflows/build.yml`

Déclenché sur push sur `main` :

1. Setup Python
2. `pip install` les dépendances
3. `python scripts/build.py all --lang fr`
4. `python scripts/build.py all --lang en`
5. Copier les PDFs et DOCX générés dans `docs/downloads/`
6. Deploy `docs/` sur GitHub Pages

---

## Contraintes ATS non négociables

1. Pas de tableau dans le DOCX
2. Pas de colonne (layout single-column uniquement)
3. Contact dans le corps, jamais en en-tête Word
4. Polices standard uniquement (Calibri, Arial, Times New Roman)
5. Pas d'image dans le DOCX
6. Dates cohérentes au format MM/YYYY
7. Titres de sections reconnaissables par les ATS
8. Score cible : 80%+ de correspondance sur les offres visées

---

## Notes de développement

- Les templates visuels (site) et ATS (DOCX/PDF) sont volontairement séparés :
  le site peut être beau, le DOCX doit être lisible par les robots.
- Le YAML pivot est la seule source à éditer. Jamais les fichiers générés.
- Prévoir un `data/jobs/` pour stocker les offres d'emploi et leur score ATS associé.
- Les fichiers DOCX et PDF générés sont committés uniquement dans `docs/downloads/`,
  pas dans `dist/` (qui reste gitignored).

---

## Démarrage

```bash
git init cv-as-code
cd cv-as-code
# Placer ce CLAUDE.md à la racine
# Lancer : claude
# Dire : "Lis le CLAUDE.md et initialise le projet complet"
```
