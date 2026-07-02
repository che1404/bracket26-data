import json
from feed.main import run


def test_run_writes_only_when_changed(tmp_path, monkeypatch):
    out = tmp_path / "results.json"
    snapshot = [{"MatchNumber": 1, "RoundNumber": 1, "DateUtc": "2026-06-11 19:00:00Z",
                 "Location": "X", "HomeTeam": "Mexico", "AwayTeam": "South Africa",
                 "Group": "Group A", "HomeTeamScore": 2, "AwayTeamScore": 1, "Winner": "Mexico"}]
    monkeypatch.setattr("feed.main.fetch_fixturedownload", lambda s: snapshot)
    monkeypatch.setattr("feed.main.fetch_football_data", lambda s, t: [])

    assert run(out) is True                      # primera escritura
    first = json.loads(out.read_text())
    assert first["results"][0]["home"] == "MEX"
    assert "generatedAt" in first

    assert run(out) is False                     # sin cambios → no reescribe
