from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text

from bola1_api.core.config import settings


@pytest.mark.postgres
def test_postgres_schema_smoke_read_only(request: pytest.FixtureRequest) -> None:
    if request.config.option.markexpr != "postgres":
        pytest.skip("PostgreSQL smoke runs only with `pytest -m postgres`")

    expected_tables = {
        "activity_events",
        "alembic_version",
        "group_members",
        "groups",
        "matches",
        "predictions",
        "teams",
        "users",
    }
    api_root = Path(__file__).resolve().parents[1]
    alembic_config = Config(str(api_root / "alembic.ini"))
    alembic_head = ScriptDirectory.from_config(alembic_config).get_current_head()

    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            schema = conn.scalar(text("select current_schema()"))
            tables = set(
                conn.execute(
                    text("select tablename from pg_tables where schemaname = 'public'"),
                ).scalars()
            )
            alembic_version = conn.scalar(text("select version_num from alembic_version limit 1"))
            team_count = conn.scalar(text("select count(*) from teams"))
            match_count = conn.scalar(text("select count(*) from matches"))
    except Exception as exc:
        pytest.fail(f"PostgreSQL smoke failed with {type(exc).__name__}", pytrace=False)

    assert settings.database_url.startswith("postgresql+psycopg://")
    assert schema == "public"
    assert expected_tables <= tables
    assert alembic_version == alembic_head
    assert team_count >= 1
    assert match_count >= 1
