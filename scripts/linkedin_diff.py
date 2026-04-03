import csv
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


def parse_linkedin_positions(csv_path: Path) -> list[dict]:
    positions = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            positions.append({
                "company": row.get("Company Name", "").strip(),
                "title": row.get("Title", "").strip(),
                "start": row.get("Started On", "").strip(),
                "end": row.get("Finished On", "").strip(),
                "location": row.get("Location", "").strip(),
            })
    return positions


def compute_diff(yaml_experience: list[dict], linkedin_positions: list[dict]) -> list[dict]:
    diffs = []

    yaml_by_company = {}
    for exp in yaml_experience:
        key = exp["company"].lower().strip()
        yaml_by_company.setdefault(key, []).append(exp)

    li_by_company = {}
    for pos in linkedin_positions:
        key = pos["company"].lower().strip()
        li_by_company.setdefault(key, []).append(pos)

    all_companies = set(yaml_by_company.keys()) | set(li_by_company.keys())

    for company in sorted(all_companies):
        yaml_entries = yaml_by_company.get(company, [])
        li_entries = li_by_company.get(company, [])

        if not yaml_entries:
            for li in li_entries:
                diffs.append({
                    "type": "missing_in_yaml",
                    "company": li["company"],
                    "title": li["title"],
                    "detail": f"Present on LinkedIn but not in YAML: {li['title']} at {li['company']}",
                })
        elif not li_entries:
            for y in yaml_entries:
                diffs.append({
                    "type": "missing_in_linkedin",
                    "company": y["company"],
                    "title": y["title"],
                    "detail": f"Present in YAML but not on LinkedIn: {y['title']} at {y['company']}",
                })
        else:
            for y in yaml_entries:
                matched = False
                for li in li_entries:
                    if _titles_similar(y["title"], li["title"]):
                        matched = True
                        if y["title"].lower() != li["title"].lower():
                            diffs.append({
                                "type": "title_mismatch",
                                "company": y["company"],
                                "title": y["title"],
                                "detail": f"Title differs — YAML: '{y['title']}' vs LinkedIn: '{li['title']}'",
                            })
                if not matched:
                    diffs.append({
                        "type": "unmatched_yaml",
                        "company": y["company"],
                        "title": y["title"],
                        "detail": f"No matching LinkedIn position for: {y['title']} at {y['company']}",
                    })

    return diffs


def _titles_similar(a: str, b: str) -> bool:
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())
    if not a_words or not b_words:
        return False
    overlap = len(a_words & b_words)
    return overlap / max(len(a_words), len(b_words)) > 0.3


def diff_linkedin(data: dict, export_path: Path):
    linkedin_positions = parse_linkedin_positions(export_path)
    diffs = compute_diff(data.get("experience", []), linkedin_positions)

    if not diffs:
        console.print("[green]YAML et LinkedIn sont synchronisés.[/green]")
        return

    table = Table(title="Différences YAML vs LinkedIn")
    table.add_column("Type", style="bold")
    table.add_column("Entreprise")
    table.add_column("Détail")

    for d in diffs:
        style = "red" if "missing" in d["type"] else "yellow"
        table.add_row(d["type"], d["company"], d["detail"], style=style)

    console.print(table)

    report = "# LinkedIn Diff Report\n\n"
    for d in diffs:
        report += f"- **{d['type']}** — {d['detail']}\n"

    report_path = Path("linkedin_diff_report.md")
    report_path.write_text(report, encoding="utf-8")
    console.print(f"\nRapport écrit dans [bold]{report_path}[/bold]")
