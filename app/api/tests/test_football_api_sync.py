from datetime import UTC, datetime
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from bola1_api.models import Match, MatchStatus, Team
from bola1_api.services import football_api


def _raw_match(
    *,
    match_id: int | None = 1001,
    home_tla: str = "ESP",
    away_tla: str = "KSA",
    status: str = "FINISHED",
    home_score: int | None = 4,
    away_score: int | None = 0,
    utc_date: str = "2026-06-14T14:00:00Z",
) -> dict[str, Any]:
    raw: dict[str, Any] = {
        "utcDate": utc_date,
        "status": status,
        "stage": "GROUP_STAGE",
        "group": "Group D",
        "venue": "Mercedes-Benz Stadium, Atlanta",
        "homeTeam": {"tla": home_tla, "name": home_tla},
        "awayTeam": {"tla": away_tla, "name": away_tla},
        "score": {"fullTime": {"home": home_score, "away": away_score}},
    }
    if match_id is not None:
        raw["id"] = match_id
    return raw


@pytest.fixture(autouse=True)
def _configure_football_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(football_api.settings, "football_api_base_url", "https://example.test")
    monkeypatch.setattr(football_api.settings, "football_api_key", "test-key")
    monkeypatch.setattr(football_api, "_last_sync_at", None)


def _run_sync(db: Session, monkeypatch: pytest.MonkeyPatch, raws: list[dict[str, Any]]) -> dict[str, int]:
    monkeypatch.setattr(football_api, "_fetch_raw_matches", lambda competition_id: raws)
    monkeypatch.setattr(football_api, "_last_sync_at", None)
    result = football_api.sync_matches(db)
    db.commit()
    return result


def test_sync_creates_match_with_external_id(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    _run_sync(db, monkeypatch, [_raw_match(match_id=2001)])

    match = db.scalar(select(Match))
    assert match is not None
    assert match.external_id == "2001"
    assert match.home_score == 4
    assert match.away_score == 0
    assert match.status == MatchStatus.finished.value


def test_sync_twice_with_rescheduled_kickoff_does_not_duplicate(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    _run_sync(
        db,
        monkeypatch,
        [_raw_match(match_id=3001, status="SCHEDULED", home_score=None, away_score=None, utc_date="2026-06-14T14:00:00Z")],
    )
    # Provider reschedules kickoff by two hours — same external id.
    _run_sync(
        db,
        monkeypatch,
        [_raw_match(match_id=3001, status="SCHEDULED", home_score=None, away_score=None, utc_date="2026-06-14T16:00:00Z")],
    )

    matches = list(db.scalars(select(Match)))
    assert len(matches) == 1
    assert matches[0].kickoff_at.replace(tzinfo=UTC) == datetime(2026, 6, 14, 16, 0, tzinfo=UTC)


def test_sync_without_external_id_falls_back_to_team_and_time_window(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    _run_sync(db, monkeypatch, [_raw_match(match_id=None, status="SCHEDULED", home_score=None, away_score=None)])
    _run_sync(db, monkeypatch, [_raw_match(match_id=None, status="IN_PLAY", home_score=1, away_score=0)])

    matches = list(db.scalars(select(Match)))
    assert len(matches) == 1
    assert matches[0].status == MatchStatus.live.value


def test_sync_corrects_score_after_match_already_finished(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    _run_sync(db, monkeypatch, [_raw_match(match_id=4001, status="FINISHED", home_score=5, away_score=0)])
    _run_sync(db, monkeypatch, [_raw_match(match_id=4001, status="FINISHED", home_score=4, away_score=0)])

    match = db.scalar(select(Match))
    assert match is not None
    assert (match.home_score, match.away_score) == (4, 0)


def test_sync_does_not_regress_finished_match_status_or_score(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    _run_sync(db, monkeypatch, [_raw_match(match_id=5001, status="FINISHED", home_score=4, away_score=0)])
    # Provider hiccup briefly reports the match as still in play.
    _run_sync(db, monkeypatch, [_raw_match(match_id=5001, status="IN_PLAY", home_score=4, away_score=0)])

    match = db.scalar(select(Match))
    assert match is not None
    assert match.status == MatchStatus.finished.value
    assert (match.home_score, match.away_score) == (4, 0)


def test_sync_ignores_finished_status_without_score(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    _run_sync(db, monkeypatch, [_raw_match(match_id=6001, status="FINISHED", home_score=4, away_score=0)])
    _run_sync(db, monkeypatch, [_raw_match(match_id=6001, status="FINISHED", home_score=None, away_score=None)])

    match = db.scalar(select(Match))
    assert match is not None
    assert (match.home_score, match.away_score) == (4, 0)


def test_sync_normalizes_curacao_tla_alias(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    _run_sync(
        db,
        monkeypatch,
        [_raw_match(match_id=7001, home_tla="CUR", away_tla="JPN", status="SCHEDULED", home_score=None, away_score=None)],
    )

    team = db.scalar(select(Team).where(Team.code == "CUW"))
    assert team is not None
    assert db.scalar(select(Team).where(Team.code == "CUR")) is None
