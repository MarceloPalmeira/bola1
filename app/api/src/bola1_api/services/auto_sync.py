"""Background task: auto-sync match data only when live or imminent matches exist.

Logic:
- Polls the DB every 60 seconds.
- If a live match exists, or a match kicks off within 90 minutes → syncs.
- Otherwise → sleeps, no external API calls.
- The 300-second cooldown inside football_api.sync_matches limits actual syncs
  to one every 5 minutes even if polls happen more frequently.
- Disabled silently when FOOTBALL_API_KEY / FOOTBALL_API_BASE_URL are absent.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from bola1_api.core.config import settings
from bola1_api.db.session import SessionLocal
from bola1_api.models import Match, MatchStatus
from bola1_api.services.football_api import (
    FootballApiCooldown,
    FootballApiError,
    FootballApiNotConfigured,
    sync_matches,
)
from bola1_api.services.scoring import recalculate_match_points

logger = logging.getLogger(__name__)

_POLL_INTERVAL_SECONDS = 60
_WINDOW_BEFORE_KICKOFF = timedelta(minutes=90)
_WINDOW_AFTER_KICKOFF = timedelta(hours=3)


def _should_sync() -> bool:
    with SessionLocal() as db:
        now = datetime.now(UTC)

        live = db.scalar(
            select(Match).where(Match.status == MatchStatus.live.value).limit(1)
        )
        if live:
            return True

        imminent = db.scalar(
            select(Match).where(
                Match.status == MatchStatus.upcoming.value,
                Match.kickoff_at >= now,
                Match.kickoff_at <= now + _WINDOW_BEFORE_KICKOFF,
            ).limit(1)
        )
        if imminent:
            return True

        # Partida que já deveria ter começado mas o DB ainda não atualizou para live/finished
        in_progress_window = db.scalar(
            select(Match).where(
                Match.status != MatchStatus.finished.value,
                Match.kickoff_at >= now - _WINDOW_AFTER_KICKOFF,
                Match.kickoff_at < now,
            ).limit(1)
        )
        return in_progress_window is not None


def _sync_now() -> dict[str, int] | None:
    with SessionLocal() as db:
        try:
            result = sync_matches(db)
            for match in db.query(Match).filter_by(status=MatchStatus.finished.value):
                recalculate_match_points(db, match=match)
            db.commit()
            return result
        except FootballApiCooldown:
            return None
        except FootballApiNotConfigured:
            return None
        except FootballApiError as exc:
            logger.warning("[auto_sync] API error: %s", exc)
            return None


async def run_auto_sync_loop() -> None:
    if not settings.football_api_key or not settings.football_api_base_url:
        logger.info("[auto_sync] Credentials not configured — auto-sync disabled")
        return

    logger.info(
        "[auto_sync] Started — poll every %ds, sync window %s before kickoff",
        _POLL_INTERVAL_SECONDS,
        _WINDOW_BEFORE_KICKOFF,
    )

    loop = asyncio.get_running_loop()
    while True:
        await asyncio.sleep(_POLL_INTERVAL_SECONDS)
        try:
            active = await loop.run_in_executor(None, _should_sync)
            if not active:
                continue
            result = await loop.run_in_executor(None, _sync_now)
            if result is not None:
                logger.info(
                    "[auto_sync] Sync complete — synced=%d skipped=%d",
                    result.get("synced", 0),
                    result.get("skipped", 0),
                )
        except Exception:
            logger.exception("[auto_sync] Unexpected error in sync loop")
