"""Hard gate: results.json must never be published if any invariant fails."""

STATUSES = {"SCHEDULED", "IN_PLAY", "FINISHED"}
# WC2026: 1-72 son grupos. Un FINISHED sin ganador (empate) solo es legal ahí; en KO
# lo decide penaltis, así que un FINISHED-draw en KO debe hacer saltar el gate.
GROUP_STAGE_MAX_MATCH = 72


def validate(payload: dict, valid_match_numbers: set[int], valid_team_ids: set[str]) -> None:
    if payload.get("schemaVersion") != 1:
        raise ValueError(f"unsupported schemaVersion: {payload.get('schemaVersion')}")
    seen: set[int] = set()
    for r in payload["results"]:
        n = r["matchNumber"]
        if n not in valid_match_numbers:
            raise ValueError(f"unknown matchNumber {n}")
        if n in seen:
            raise ValueError(f"duplicate matchNumber {n}")
        seen.add(n)
        if r["status"] not in STATUSES:
            raise ValueError(f"match {n}: bad status {r['status']}")
        for side in ("home", "away"):
            if r[side] is not None and r[side] not in valid_team_ids:
                raise ValueError(f"match {n}: unknown team {r[side]}")
        if r["home"] is None and r["away"] is None:
            raise ValueError(f"match {n}: both sides null")
        if (r["home"] is None or r["away"] is None) and r["status"] != "SCHEDULED":
            raise ValueError(f"match {n}: null side only allowed when SCHEDULED")
        if r["home"] is not None and r["away"] is not None and r["home"] == r["away"]:
            raise ValueError(f"match {n}: home == away")
        if r["status"] == "FINISHED":
            if r["homeScore"] is None or r["awayScore"] is None:
                raise ValueError(f"match {n}: FINISHED requires scores")
            if r["winner"] is None:
                if r["homeScore"] != r["awayScore"]:
                    raise ValueError(f"match {n}: FINISHED without winner must be a draw")
                if n > GROUP_STAGE_MAX_MATCH:
                    raise ValueError(f"match {n}: knockout draw cannot be FINISHED without a winner")
            elif r["winner"] not in (r["home"], r["away"]):
                raise ValueError(f"match {n}: winner not playing")
        if r["status"] == "SCHEDULED":
            if r["homeScore"] is not None or r["awayScore"] is not None or r["winner"] is not None:
                raise ValueError(f"match {n}: SCHEDULED must have no result")
        if r["status"] == "IN_PLAY" and r["winner"] is not None:
            raise ValueError(f"match {n}: IN_PLAY cannot have winner")
