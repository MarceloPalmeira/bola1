from datetime import UTC, datetime

from bola1_api.db.session import SessionLocal
from bola1_api.models import Match, MatchPhase, MatchStatus, Team
from bola1_api.repositories.matches import get_team_by_code

TEAMS = [
    ("Brasil", "BRA", "🇧🇷"),
    ("Argentina", "ARG", "🇦🇷"),
    ("França", "FRA", "🇫🇷"),
    ("Alemanha", "GER", "🇩🇪"),
    ("Espanha", "ESP", "🇪🇸"),
    ("Inglaterra", "ENG", "🏴"),
    ("Portugal", "POR", "🇵🇹"),
    ("Holanda", "NED", "🇳🇱"),
    ("México", "MEX", "🇲🇽"),
    ("Canadá", "CAN", "🇨🇦"),
    ("EUA", "USA", "🇺🇸"),
    ("Japão", "JPN", "🇯🇵"),
]

MATCHES = [
    ("MEX", "CAN", "2026-06-11T17:00:00+00:00", "Estádio Azteca, Cidade do México", "A"),
    ("USA", "ARG", "2026-06-12T20:00:00+00:00", "MetLife Stadium, Nova York", "B"),
    ("BRA", "JPN", "2026-06-13T17:00:00+00:00", "SoFi Stadium, Los Angeles", "C"),
    ("GER", "ESP", "2026-06-14T14:00:00+00:00", "Mercedes-Benz Stadium, Atlanta", "D"),
]


def seed() -> None:
    db = SessionLocal()
    try:
        for name, code, flag in TEAMS:
            if not get_team_by_code(db, code):
                db.add(Team(name=name, code=code, flag=flag))
        db.flush()

        for home_code, away_code, kickoff, venue, world_cup_group in MATCHES:
            home_team = get_team_by_code(db, home_code)
            away_team = get_team_by_code(db, away_code)
            if not home_team or not away_team:
                continue
            exists = (
                db.query(Match)
                .filter(
                    Match.home_team_id == home_team.id,
                    Match.away_team_id == away_team.id,
                    Match.kickoff_at == datetime.fromisoformat(kickoff),
                )
                .first()
            )
            if exists:
                continue
            db.add(
                Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    kickoff_at=datetime.fromisoformat(kickoff).astimezone(UTC),
                    venue=venue,
                    phase=MatchPhase.group_stage.value,
                    world_cup_group=world_cup_group,
                    status=MatchStatus.upcoming.value,
                )
            )

        db.commit()
        print("Seed completed")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
