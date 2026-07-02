"""Builds the results.json payload from a fixturedownload snapshot."""


def build_results(snapshot: list[dict], team_ids: dict[str, str], valid_match_numbers: set[int]) -> dict:
    results = []
    for m in snapshot:
        if m["MatchNumber"] not in valid_match_numbers:
            continue
        home = team_ids.get(m["HomeTeam"])
        away = team_ids.get(m["AwayTeam"])
        if home is None or away is None:
            continue  # cruce aún no conocido (placeholder del feed) → se omite
        home_score, away_score = m["HomeTeamScore"], m["AwayTeamScore"]
        winner = team_ids.get(m.get("Winner") or "")
        if winner is not None:
            status = "FINISHED"
        elif home_score is not None and away_score is not None and home_score == away_score:
            status = "FINISHED"  # empate terminado (feed: Winner "Draw") → sin ganador de equipo
        elif home_score is not None or away_score is not None:
            status = "IN_PLAY"
        else:
            status = "SCHEDULED"
        results.append({
            "matchNumber": m["MatchNumber"], "home": home, "away": away,
            "homeScore": home_score if status != "SCHEDULED" else None,
            "awayScore": away_score if status != "SCHEDULED" else None,
            "winner": winner, "status": status,
        })
    results.sort(key=lambda r: r["matchNumber"])
    return {"schemaVersion": 1, "results": results}
