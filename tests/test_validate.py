import pytest
from feed.validate import validate

VALID_M = {1, 73}
VALID_T = {"MEX", "RSA", "GER"}


def entry(**over):
    base = {"matchNumber": 1, "home": "MEX", "away": "RSA",
            "homeScore": 2, "awayScore": 1, "winner": "MEX", "status": "FINISHED"}
    return base | over


def payload(*entries):
    return {"schemaVersion": 1, "results": list(entries)}


def test_valid_payload_passes():
    validate(payload(entry()), VALID_M, VALID_T)


@pytest.mark.parametrize("bad", [
    entry(matchNumber=999),                                  # match desconocido
    entry(home="XXX"),                                       # teamID desconocido
    entry(winner="GER"),                                     # winner no juega el partido
    entry(status="FINISHED", winner=None),                   # FINISHED sin winner
    entry(status="FINISHED", homeScore=None),                # FINISHED sin score
    entry(status="SCHEDULED"),                                # SCHEDULED con scores/winner
    entry(status="LIMBO"),                                    # status inválido
    entry(home="MEX", away="MEX"),                            # mismo equipo
])
def test_invalid_entries_raise(bad):
    with pytest.raises(ValueError):
        validate(payload(bad), VALID_M, VALID_T)


def test_finished_draw_with_null_winner_passes():
    validate(payload(entry(status="FINISHED", winner=None, homeScore=1, awayScore=1)),
             VALID_M, VALID_T)


def test_finished_draw_in_knockout_raises():
    with pytest.raises(ValueError):
        validate(payload(entry(matchNumber=73, status="FINISHED",
                               winner=None, homeScore=1, awayScore=1)),
                 VALID_M, VALID_T)


def test_partial_scheduled_null_side_passes():
    validate(payload(entry(status="SCHEDULED", away=None,
                           homeScore=None, awayScore=None, winner=None)),
             VALID_M, VALID_T)


def test_finished_with_null_side_raises():
    with pytest.raises(ValueError):
        validate(payload(entry(status="FINISHED", away=None)), VALID_M, VALID_T)


def test_both_sides_null_raises():
    with pytest.raises(ValueError):
        validate(payload(entry(status="SCHEDULED", home=None, away=None,
                               homeScore=None, awayScore=None, winner=None)),
                 VALID_M, VALID_T)


def test_duplicate_match_numbers_raise():
    with pytest.raises(ValueError):
        validate(payload(entry(), entry()), VALID_M, VALID_T)


def test_wrong_schema_version_raises():
    with pytest.raises(ValueError):
        validate({"schemaVersion": 2, "results": []}, VALID_M, VALID_T)
