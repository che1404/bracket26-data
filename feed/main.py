"""Entry point: fetch → build → arbitrate → validate → write-if-changed."""
import datetime
import json
import os
import sys
from pathlib import Path

import requests

from feed.build import build_results
from feed.sources import arbitrate, fetch_fixturedownload, fetch_football_data
from feed.validate import validate

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"


def load_reference() -> tuple[dict[str, str], set[int], set[str], dict[int, str]]:
    meta = json.loads((REFERENCE / "team-meta.json").read_text())
    team_ids = {name: entry["id"] for name, entry in meta.items()}
    fixtures = json.loads((REFERENCE / "fixtures.json").read_text())["matches"]
    numbers = {m["matchNumber"] for m in fixtures}
    kickoffs = {m["matchNumber"]: m["kickoffUtc"] for m in fixtures}
    return team_ids, numbers, set(team_ids.values()), kickoffs


def run(out_path: Path) -> bool:
    team_ids, numbers, ids, kickoffs = load_reference()
    session = requests.Session()
    snapshot = fetch_fixturedownload(session)
    payload = build_results(snapshot, team_ids, numbers)
    token = os.environ.get("FOOTBALL_DATA_TOKEN", "")
    if token:
        payload["results"] = arbitrate(payload["results"], fetch_football_data(session, token), kickoffs)
    validate(payload, numbers, ids)

    previous = None
    if out_path.exists():
        previous = json.loads(out_path.read_text())
        previous.pop("generatedAt", None)
    if previous == payload:
        return False
    payload["generatedAt"] = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    out_path.write_text(json.dumps(payload, indent=1) + "\n")
    return True


if __name__ == "__main__":
    changed = run(ROOT / "results.json")
    print(f"results.json {'updated' if changed else 'unchanged'}")
    sys.exit(0)
