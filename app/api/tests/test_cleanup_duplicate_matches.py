from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from bola1_api.models import ActivityEvent, Group, Match, MatchPhase, MatchStatus, Prediction, Team, User
from bola1_api.scripts.cleanup_duplicate_matches import cleanup


def _make_team(db: Session, name: str, code: str) -> Team:
    team = Team(name=name, code=code, flag="🏳")
    db.add(team)
    db.flush()
    return team


def _make_user(db: Session, email: str) -> User:
    user = User(email=email, password_hash="x", nickname=email.split("@")[0])
    db.add(user)
    db.flush()
    return user


def _make_group(db: Session, owner: User) -> Group:
    group = Group(name="Test Group", code=f"code-{owner.id}", created_by_id=owner.id)
    db.add(group)
    db.flush()
    return group


def _make_match(
    db: Session,
    *,
    home: Team,
    away: Team,
    kickoff_at: datetime,
    status: str = MatchStatus.upcoming.value,
    home_score: int | None = None,
    away_score: int | None = None,
    venue: str = "A definir",
    external_id: str | None = None,
) -> Match:
    match = Match(
        home_team_id=home.id,
        away_team_id=away.id,
        kickoff_at=kickoff_at,
        venue=venue,
        phase=MatchPhase.group_stage.value,
        world_cup_group="D",
        status=status,
        home_score=home_score,
        away_score=away_score,
        external_id=external_id,
    )
    db.add(match)
    db.flush()
    return match


def test_cleanup_merges_duplicates_and_repoints_prediction(db: Session) -> None:
    home, away = _make_team(db, "Espanha", "ESP2"), _make_team(db, "Alemanha", "GER2")
    user = _make_user(db, "fan@example.com")
    group = _make_group(db, user)

    stale = _make_match(db, home=home, away=away, kickoff_at=datetime(2026, 6, 14, 14, 0, tzinfo=UTC))
    canonical = _make_match(
        db,
        home=home,
        away=away,
        kickoff_at=datetime(2026, 6, 14, 16, 0, tzinfo=UTC),
        status=MatchStatus.finished.value,
        home_score=2,
        away_score=1,
        external_id="9999",
    )
    prediction = Prediction(match_id=stale.id, group_id=group.id, user_id=user.id, home_score=1, away_score=1)
    db.add(prediction)
    db.commit()

    result = cleanup(db)

    assert result["duplicate_groups_merged"] == 1
    assert result["matches_deleted"] == 1

    remaining = list(db.scalars(select(Match)))
    assert len(remaining) == 1
    assert remaining[0].id == canonical.id

    db.refresh(prediction)
    assert prediction.match_id == canonical.id
    assert prediction.points == 0  # 1-1 predicted vs 2-1 actual -> miss


def test_cleanup_drops_conflicting_duplicate_prediction_without_error(db: Session) -> None:
    home, away = _make_team(db, "Brasil2", "BRA2"), _make_team(db, "Croacia2", "CRO2")
    user = _make_user(db, "duplicado@example.com")
    group = _make_group(db, user)

    dup = _make_match(db, home=home, away=away, kickoff_at=datetime(2026, 6, 15, 14, 0, tzinfo=UTC))
    canonical = _make_match(
        db,
        home=home,
        away=away,
        kickoff_at=datetime(2026, 6, 15, 14, 30, tzinfo=UTC),
        status=MatchStatus.finished.value,
        home_score=1,
        away_score=0,
        external_id="8888",
    )
    pred_on_dup = Prediction(match_id=dup.id, group_id=group.id, user_id=user.id, home_score=2, away_score=0)
    pred_on_canonical = Prediction(match_id=canonical.id, group_id=group.id, user_id=user.id, home_score=1, away_score=0)
    db.add_all([pred_on_dup, pred_on_canonical])
    db.flush()
    event = ActivityEvent(group_id=group.id, user_id=user.id, type="prediction", match_id=dup.id, prediction_id=pred_on_dup.id)
    db.add(event)
    db.commit()

    result = cleanup(db)

    assert result["matches_deleted"] == 1
    predictions = list(db.scalars(select(Prediction).where(Prediction.user_id == user.id, Prediction.group_id == group.id)))
    assert len(predictions) == 1
    assert predictions[0].id == pred_on_canonical.id

    db.refresh(event)
    assert event.match_id == canonical.id
    assert event.prediction_id is None


def test_cleanup_is_idempotent(db: Session) -> None:
    home, away = _make_team(db, "Franca2", "FRA2"), _make_team(db, "Marrocos2", "MAR2")
    _make_match(db, home=home, away=away, kickoff_at=datetime(2026, 6, 16, 14, 0, tzinfo=UTC))
    _make_match(
        db,
        home=home,
        away=away,
        kickoff_at=datetime(2026, 6, 16, 14, 10, tzinfo=UTC),
        status=MatchStatus.finished.value,
        home_score=2,
        away_score=0,
    )
    db.commit()

    first = cleanup(db)
    second = cleanup(db)

    assert first["matches_deleted"] == 1
    assert second["duplicate_groups_merged"] == 0
    assert second["matches_deleted"] == 0
    assert len(list(db.scalars(select(Match)))) == 1


def test_cleanup_fixes_espanha_arabia_saudita_score(db: Session) -> None:
    home, away = _make_team(db, "Espanha", "ESP"), _make_team(db, "Arábia Saudita", "KSA")
    _make_match(
        db,
        home=home,
        away=away,
        kickoff_at=datetime(2026, 6, 14, 14, 0, tzinfo=UTC),
        status=MatchStatus.finished.value,
        home_score=5,
        away_score=0,
    )
    db.commit()

    result = cleanup(db)
    match = db.scalar(select(Match).where(Match.home_team_id == home.id, Match.away_team_id == away.id))

    assert result["scores_corrected"] == 1
    assert (match.home_score, match.away_score) == (4, 0)
    assert match.status == MatchStatus.finished.value

    second = cleanup(db)
    assert second["scores_corrected"] == 0


def test_cleanup_fixes_score_when_teams_are_flipped(db: Session) -> None:
    home, away = _make_team(db, "Arábia Saudita", "KSA"), _make_team(db, "Espanha", "ESP")
    _make_match(
        db,
        home=home,
        away=away,
        kickoff_at=datetime(2026, 6, 14, 14, 0, tzinfo=UTC),
        status=MatchStatus.finished.value,
        home_score=0,
        away_score=5,
    )
    db.commit()

    cleanup(db)
    match = db.scalar(select(Match).where(Match.home_team_id == home.id, Match.away_team_id == away.id))

    assert (match.home_score, match.away_score) == (0, 4)


def test_cleanup_merges_duplicate_team_created_under_tla_alias(db: Session) -> None:
    # Reproduces the real production bug: the external API returned "URU"
    # for Uruguay on some syncs and "URY" on others, creating two Team rows
    # and, transitively, a duplicate Match per fixture under each team_id.
    ksa = _make_team(db, "Arábia Saudita", "KSA3")
    ury = _make_team(db, "Uruguai", "URY")
    uru = _make_team(db, "Uruguay", "URU")
    user = _make_user(db, "torcedor@example.com")
    group = _make_group(db, user)

    canonical = _make_match(
        db,
        home=ksa,
        away=ury,
        kickoff_at=datetime(2026, 6, 15, 22, 0, tzinfo=UTC),
        status=MatchStatus.finished.value,
        home_score=1,
        away_score=1,
    )
    legacy_dup = _make_match(
        db,
        home=ksa,
        away=uru,
        kickoff_at=datetime(2026, 6, 15, 22, 0, tzinfo=UTC),
        status=MatchStatus.finished.value,
        home_score=1,
        away_score=1,
    )
    prediction = Prediction(match_id=canonical.id, group_id=group.id, user_id=user.id, home_score=1, away_score=1)
    db.add(prediction)
    db.commit()

    result = cleanup(db)

    assert {"from_code": "URU", "to_code": "URY", "matches_repointed": 1} in result["team_merges"]
    assert db.scalar(select(Team).where(Team.code == "URU")) is None
    remaining_matches = list(db.scalars(select(Match).where(Match.home_team_id == ksa.id)))
    assert len(remaining_matches) == 1
    assert remaining_matches[0].away_team_id == ury.id
    db.refresh(prediction)
    assert prediction.match_id == canonical.id


def test_cleanup_dry_run_previews_without_committing(db: Session) -> None:
    home, away = _make_team(db, "Portugal2", "POR2"), _make_team(db, "Gana2", "GHA2")
    stale = _make_match(db, home=home, away=away, kickoff_at=datetime(2026, 6, 18, 14, 0, tzinfo=UTC))
    canonical = _make_match(
        db,
        home=home,
        away=away,
        kickoff_at=datetime(2026, 6, 18, 14, 30, tzinfo=UTC),
        status=MatchStatus.finished.value,
        home_score=3,
        away_score=1,
    )
    db.commit()

    preview = cleanup(db, dry_run=True)
    assert preview["dry_run"] is True
    assert preview["duplicate_groups_merged"] == 1
    assert len(list(db.scalars(select(Match)))) == 2, "dry-run must not delete anything"
    assert db.get(Match, stale.id) is not None
    assert db.get(Match, canonical.id) is not None

    real_result = cleanup(db)
    assert real_result["dry_run"] is False
    assert real_result["duplicate_groups_merged"] == 1
    assert len(list(db.scalars(select(Match)))) == 1
