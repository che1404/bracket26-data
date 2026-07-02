import json
from pathlib import Path
from feed.build import build_results

FIXTURES = Path(__file__).parent / "fixtures"
TEAM_IDS = {"Mexico": "MEX", "South Africa": "RSA", "Germany": "GER", "Spain": "ESP", "France": "FRA"}
VALID = {1, 73, 74, 90}


def load_snapshot():
    return json.loads((FIXTURES / "snapshot_sample.json").read_text())


def test_finished_match_maps_scores_and_winner():
    out = build_results(load_snapshot(), TEAM_IDS, VALID)
    m1 = next(r for r in out["results"] if r["matchNumber"] == 1)
    assert m1 == {"matchNumber": 1, "home": "MEX", "away": "RSA",
                  "homeScore": 2, "awayScore": 1, "winner": "MEX", "status": "FINISHED"}


def test_known_pairing_without_result_is_scheduled():
    out = build_results(load_snapshot(), TEAM_IDS, VALID)
    m73 = next(r for r in out["results"] if r["matchNumber"] == 73)
    assert m73["home"] == "MEX" and m73["away"] == "GER"
    assert m73["status"] == "SCHEDULED"
    assert m73["homeScore"] is None and m73["winner"] is None


def test_draw_with_explicit_winner_is_finished():
    out = build_results(load_snapshot(), TEAM_IDS, VALID)
    m74 = next(r for r in out["results"] if r["matchNumber"] == 74)
    assert m74["winner"] == "ESP" and m74["status"] == "FINISHED"


def test_unknown_pairing_is_omitted():
    out = build_results(load_snapshot(), TEAM_IDS, VALID)
    assert all(r["matchNumber"] != 90 for r in out["results"])


def test_scores_without_winner_is_in_play():
    snap = load_snapshot()
    snap[0]["Winner"] = ""
    out = build_results(snap, TEAM_IDS, VALID)
    m1 = next(r for r in out["results"] if r["matchNumber"] == 1)
    assert m1["status"] == "IN_PLAY" and m1["winner"] is None


def test_draw_is_finished_with_null_winner():
    snap = load_snapshot()
    snap[0]["Winner"] = "Draw"
    snap[0]["HomeTeamScore"], snap[0]["AwayTeamScore"] = 1, 1
    out = build_results(snap, TEAM_IDS, VALID)
    m1 = next(r for r in out["results"] if r["matchNumber"] == 1)
    assert m1["status"] == "FINISHED" and m1["winner"] is None
    assert m1["homeScore"] == 1 and m1["awayScore"] == 1


def test_schema_version_present():
    assert build_results(load_snapshot(), TEAM_IDS, VALID)["schemaVersion"] == 1
