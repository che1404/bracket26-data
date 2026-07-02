"""HTTP sources: fixturedownload (primary) and football-data.org (arbiter)."""
import sys
import time

FIXTUREDOWNLOAD_URL = "https://fixturedownload.com/feed/json/fifa-world-cup-2026"
FOOTBALL_DATA_URL = "https://api.football-data.org/v4/competitions/WC/matches"
UA = {"User-Agent": "Mozilla/5.0 (bracket26-data feed; +https://github.com/che1404/bracket26-data)"}


class SourceError(Exception):
    pass


def fetch_fixturedownload(session) -> list[dict]:
    for attempt, delay in enumerate((2, 8, 0)):
        try:
            resp = session.get(FIXTUREDOWNLOAD_URL, headers=UA, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:  # noqa: BLE001 — cualquier fallo de red/HTTP reintenta
            print(f"[sources] fixturedownload attempt {attempt + 1} failed: {e}", file=sys.stderr)
            if delay:
                time.sleep(delay)
    raise SourceError("fixturedownload unreachable after 3 attempts")


def fetch_football_data(session, token: str) -> list[dict]:
    try:
        resp = session.get(FOOTBALL_DATA_URL, headers={"X-Auth-Token": token}, timeout=30)
        resp.raise_for_status()
        return resp.json()["matches"]
    except Exception as e:  # noqa: BLE001 — el árbitro es opcional
        print(f"[sources] football-data unavailable: {e}", file=sys.stderr)
        return []


def arbitrate(results: list[dict], fd_matches: list[dict], kickoffs: dict[int, str]) -> list[dict]:
    out = []
    for r in results:
        if r["status"] != "FINISHED":
            out.append(r)
            continue
        kickoff = kickoffs.get(r["matchNumber"])
        candidates = [m for m in fd_matches if m.get("utcDate") == kickoff]
        if len(candidates) != 1:
            out.append(r)
            continue
        score = candidates[0]["score"]
        ft = score.get("fullTime", {})
        fd_winner = {"HOME_TEAM": r["home"], "AWAY_TEAM": r["away"]}.get(score.get("winner"))
        if fd_winner and (ft.get("home") != r["homeScore"] or ft.get("away") != r["awayScore"]
                          or fd_winner != r["winner"]):
            print(f"[sources] arbiter override for match {r['matchNumber']}", file=sys.stderr)
            out.append(r | {"homeScore": ft.get("home"), "awayScore": ft.get("away"), "winner": fd_winner})
        else:
            out.append(r)
    return out
