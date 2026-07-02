"""Hard gate: results.json must never be published if any invariant fails."""

STATUSES = {"SCHEDULED", "IN_PLAY", "FINISHED"}


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
            if r[side] not in valid_team_ids:
                raise ValueError(f"match {n}: unknown team {r[side]}")
        if r["home"] == r["away"]:
            raise ValueError(f"match {n}: home == away")
        if r["status"] == "FINISHED":
            if r["homeScore"] is None or r["awayScore"] is None or r["winner"] is None:
                raise ValueError(f"match {n}: FINISHED requires scores and winner")
            if r["winner"] not in (r["home"], r["away"]):
                raise ValueError(f"match {n}: winner not playing")
        if r["status"] == "SCHEDULED":
            if r["homeScore"] is not None or r["awayScore"] is not None or r["winner"] is not None:
                raise ValueError(f"match {n}: SCHEDULED must have no result")
        if r["status"] == "IN_PLAY" and r["winner"] is not None:
            raise ValueError(f"match {n}: IN_PLAY cannot have winner")
