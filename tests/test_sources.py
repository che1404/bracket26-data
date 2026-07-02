import pytest
from feed.sources import fetch_fixturedownload, arbitrate, SourceError


class FakeResponse:
    def __init__(self, status=200, payload=None):
        self.status_code = status
        self._payload = payload or []

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, responses):
        self.responses, self.calls = list(responses), 0

    def get(self, url, **kw):
        self.calls += 1
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def test_fetch_retries_then_succeeds(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    session = FakeSession([TimeoutError(), FakeResponse(payload=[{"MatchNumber": 1}])])
    assert fetch_fixturedownload(session) == [{"MatchNumber": 1}]
    assert session.calls == 2


def test_fetch_gives_up_after_three(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    session = FakeSession([TimeoutError()] * 3)
    with pytest.raises(SourceError):
        fetch_fixturedownload(session)


FD = [{"utcDate": "2026-06-28T19:00:00Z",
       "score": {"winner": "AWAY_TEAM", "fullTime": {"home": 0, "away": 2}}}]
KICKOFFS = {73: "2026-06-28T19:00:00Z"}


def entry(**over):
    base = {"matchNumber": 73, "home": "MEX", "away": "GER",
            "homeScore": 2, "awayScore": 1, "winner": "MEX", "status": "FINISHED"}
    return base | over


def test_arbiter_overrides_discrepant_finished():
    out = arbitrate([entry()], FD, KICKOFFS)
    assert out[0]["winner"] == "GER" and out[0]["homeScore"] == 0 and out[0]["awayScore"] == 2


def test_arbiter_keeps_agreeing_result():
    fd = [{"utcDate": "2026-06-28T19:00:00Z",
           "score": {"winner": "HOME_TEAM", "fullTime": {"home": 2, "away": 1}}}]
    assert arbitrate([entry()], fd, KICKOFFS) == [entry()]


def test_arbiter_ignores_ambiguous_kickoff():
    assert arbitrate([entry()], FD + FD, KICKOFFS) == [entry()]


def test_arbiter_skips_non_finished():
    e = entry(status="IN_PLAY", winner=None)
    assert arbitrate([e], FD, KICKOFFS) == [e]
