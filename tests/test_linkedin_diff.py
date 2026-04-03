import csv
from pathlib import Path
from scripts.linkedin_diff import parse_linkedin_positions, compute_diff


def _write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def test_parse_linkedin_positions(tmp_path):
    csv_path = tmp_path / "Positions.csv"
    _write_csv(csv_path, [
        {"Company Name": "Acme", "Title": "Developer", "Started On": "Jan 2020", "Finished On": "Dec 2021", "Location": "Paris"},
    ])
    positions = parse_linkedin_positions(csv_path)
    assert len(positions) == 1
    assert positions[0]["company"] == "Acme"
    assert positions[0]["title"] == "Developer"


def test_compute_diff():
    yaml_exp = [
        {"title": "Dev", "company": "Acme", "startDate": "2020-01", "endDate": "2021-12"},
    ]
    linkedin_pos = [
        {"title": "Developer", "company": "Acme", "start": "Jan 2020", "end": "Dec 2021", "location": "Paris"},
    ]
    diffs = compute_diff(yaml_exp, linkedin_pos)
    assert isinstance(diffs, list)
