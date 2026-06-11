from pathlib import Path

from alembic import command
from alembic.config import Config


def test_alembic_upgrade_head_with_sqlite(tmp_path, monkeypatch) -> None:
    api_root = Path(__file__).resolve().parents[1]
    database_url = f"sqlite:///{tmp_path / 'alembic.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)

    config = Config(str(api_root / "alembic.ini"))
    config.set_main_option("script_location", str(api_root / "alembic"))

    command.upgrade(config, "head")
