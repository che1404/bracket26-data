"""Builds the results.json payload from a fixturedownload snapshot."""

# WC2026: partidos 1-72 son fase de grupos. La inferencia de empate (scores iguales sin
# ganador de equipo → FINISHED) solo aplica ahí; en KO un empate significa penaltis en curso.
GROUP_STAGE_MAX_MATCH = 72


def build_results(snapshot: list[dict], team_ids: dict[str, str], valid_match_numbers: set[int]) -> dict:
    results = []
    for m in snapshot:
        if m["MatchNumber"] not in valid_match_numbers:
            continue
        home = team_ids.get(m["HomeTeam"])
        away = team_ids.get(m["AwayTeam"])
        if home is None and away is None:
            continue  # ningún lado conocido aún (ambos placeholder) → se omite
        home_score, away_score = m["HomeTeamScore"], m["AwayTeamScore"]
        winner = team_ids.get(m.get("Winner") or "")
        is_group = m["MatchNumber"] <= GROUP_STAGE_MAX_MATCH
        if winner is not None:
            status = "FINISHED"
        elif (is_group and home_score is not None and away_score is not None
              and home_score == away_score):
            status = "FINISHED"  # empate de grupos terminado (feed: Winner "Draw") → sin ganador
        elif home_score is not None or away_score is not None:
            status = "IN_PLAY"
        else:
            status = "SCHEDULED"
        if status != "SCHEDULED" and (home is None or away is None):
            continue  # anomalía: hay resultado pero un lado no mapea → no publicar basura
        results.append({
            "matchNumber": m["MatchNumber"], "home": home, "away": away,
            "homeScore": home_score if status != "SCHEDULED" else None,
            "awayScore": away_score if status != "SCHEDULED" else None,
            "winner": winner, "status": status,
        })
    results.sort(key=lambda r: r["matchNumber"])
    return {"schemaVersion": 1, "results": results}
