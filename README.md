# CV-as-Code

CV versionné sous Git, avec un format source YAML qui génère automatiquement DOCX (ATS-friendly), PDF et un site statique.

**Site** : https://glandais.github.io/

## Installation

```bash
uv sync
bash scripts/install-hooks.sh
```

## Utilisation

```bash
# Générer tous les formats
uv run python -m scripts.build all --lang fr

# Générer un seul format
uv run python -m scripts.build docx --lang fr
uv run python -m scripts.build pdf --lang fr
uv run python -m scripts.build site --lang fr

# Scorer le CV contre une offre d'emploi
uv run python -m scripts.build ats-score --job data/jobs/offre.txt

# Comparer avec un export LinkedIn
uv run python -m scripts.build linkedin-diff --export Positions.csv
```

## Tests

```bash
uv run pytest
```

## Structure

```
data/resume.fr.yaml          # Source YAML (seul fichier à éditer)
scripts/                      # CLI et générateurs
templates/ats/                # Template HTML ATS (pour PDF)
templates/visual/             # Template HTML site
docs/                         # Site GitHub Pages (généré)
hooks/                        # Git hooks versionnés
```

## Git hooks

Le hook `pre-push` reconstruit automatiquement le DOCX, PDF et le site avant chaque push, et commite les fichiers mis à jour dans `docs/`.

Installation :

```bash
bash scripts/install-hooks.sh
```
