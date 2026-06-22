"""External football API sync service.

Environment variables required to activate:
  FOOTBALL_API_BASE_URL  – provider base URL
                           e.g. https://api.football-data.org/v4
  FOOTBALL_API_KEY       – provider auth key

Mapping targets football-data.org v4 (free tier).
To use a different provider, update the _map_* helpers below.

Admin-only endpoint: POST /api/v1/admin/matches/sync
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from bola1_api.core.config import settings
from bola1_api.db.base import new_id
from bola1_api.models import Match, MatchPhase, MatchStatus, Team
from sqlalchemy.orm import Session
from sqlalchemy import select


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class FootballApiNotConfigured(Exception):
    """Raised when required env vars are absent."""


class FootballApiError(Exception):
    """Raised on network or HTTP errors from the provider."""


class FootballApiCooldown(Exception):
    """Raised when sync is called before the cooldown period has elapsed."""


# ---------------------------------------------------------------------------
# Cooldown state (in-process; resets on server restart – sufficient for a
# single-worker admin-only tool against a rate-limited free-tier API)
# ---------------------------------------------------------------------------

_last_sync_at: datetime | None = None


def _check_and_set_cooldown() -> None:
    global _last_sync_at
    now = datetime.now(timezone.utc)
    cooldown = settings.football_api_sync_cooldown_seconds
    if _last_sync_at is not None:
        elapsed = (now - _last_sync_at).total_seconds()
        if elapsed < cooldown:
            remaining = int(cooldown - elapsed)
            raise FootballApiCooldown(
                f"Sync called too soon. Wait {remaining} more second(s) "
                f"(cooldown: {cooldown} s). Last sync: {_last_sync_at.isoformat()}"
            )
    _last_sync_at = now


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_STATUS_MAP: dict[str, MatchStatus] = {
    "SCHEDULED": MatchStatus.upcoming,
    "TIMED": MatchStatus.upcoming,
    "IN_PLAY": MatchStatus.live,
    "PAUSED": MatchStatus.live,
    "HALFTIME": MatchStatus.live,
    "EXTRA_TIME": MatchStatus.live,
    "PENALTY": MatchStatus.live,
    "FINISHED": MatchStatus.finished,
    "AWARDED": MatchStatus.finished,
    "SUSPENDED": MatchStatus.upcoming,
    "POSTPONED": MatchStatus.upcoming,
    "CANCELLED": MatchStatus.upcoming,
}

_STAGE_MAP: dict[str, MatchPhase] = {
    "GROUP_STAGE": MatchPhase.group_stage,
    "ROUND_OF_16": MatchPhase.round_of_16,
    "QUARTER_FINALS": MatchPhase.quarter_finals,
    "SEMI_FINALS": MatchPhase.semi_finals,
    "FINAL": MatchPhase.final,
}

_FLAG_MAP: dict[str, str] = {
    # Americas
    "ARG": "🇦🇷", "BOL": "🇧🇴", "BRA": "🇧🇷", "CAN": "🇨🇦",
    "CHI": "🇨🇱", "COL": "🇨🇴", "CRC": "🇨🇷", "ECU": "🇪🇨",
    "GUA": "🇬🇹", "GUY": "🇬🇾", "HAI": "🇭🇹", "HON": "🇭🇳",
    "JAM": "🇯🇲", "MEX": "🇲🇽", "PAN": "🇵🇦", "PAR": "🇵🇾",
    "PER": "🇵🇪", "TRI": "🇹🇹", "URY": "🇺🇾", "USA": "🇺🇸",
    "VEN": "🇻🇪",
    # Europe
    "ALB": "🇦🇱", "AND": "🇦🇩", "ARM": "🇦🇲", "AUT": "🇦🇹",
    "AZE": "🇦🇿", "BEL": "🇧🇪", "BIH": "🇧🇦", "BUL": "🇧🇬",
    "CRO": "🇭🇷", "CUW": "🇨🇼", "CYP": "🇨🇾", "CZE": "🇨🇿",
    "DEN": "🇩🇰", "ENG": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "ESP": "🇪🇸", "EST": "🇪🇪",
    "FIN": "🇫🇮", "FRA": "🇫🇷", "GEO": "🇬🇪", "GER": "🇩🇪",
    "GRE": "🇬🇷", "HUN": "🇭🇺", "IRL": "🇮🇪", "ISL": "🇮🇸",
    "ITA": "🇮🇹", "KAZ": "🇰🇿", "LAT": "🇱🇻", "LIE": "🇱🇮",
    "LTU": "🇱🇹", "LUX": "🇱🇺", "MDA": "🇲🇩", "MKD": "🇲🇰",
    "MLT": "🇲🇹", "MNE": "🇲🇪", "NED": "🇳🇱", "NIR": "🇬🇧",
    "NOR": "🇳🇴", "POL": "🇵🇱", "POR": "🇵🇹", "ROU": "🇷🇴",
    "RSM": "🇸🇲", "RUS": "🇷🇺", "SCO": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "SRB": "🇷🇸",
    "SUI": "🇨🇭", "SVK": "🇸🇰", "SVN": "🇸🇮", "SWE": "🇸🇪",
    "TUR": "🇹🇷", "UKR": "🇺🇦", "WAL": "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
    # Africa
    "ALG": "🇩🇿", "ANG": "🇦🇴", "BEN": "🇧🇯", "BFA": "🇧🇫",
    "BUR": "🇧🇮", "CIV": "🇨🇮", "CMR": "🇨🇲", "COD": "🇨🇩",
    "CPV": "🇨🇻", "EGY": "🇪🇬", "ETH": "🇪🇹", "GAB": "🇬🇦",
    "GHA": "🇬🇭", "GUI": "🇬🇳", "KEN": "🇰🇪", "LBA": "🇱🇾",
    "MAD": "🇲🇬", "MAR": "🇲🇦", "MLI": "🇲🇱", "MOZ": "🇲🇿",
    "MRI": "🇲🇺", "MTN": "🇲🇷", "NGA": "🇳🇬", "RSA": "🇿🇦",
    "RWA": "🇷🇼", "SEN": "🇸🇳", "SLE": "🇸🇱", "SOM": "🇸🇴",
    "TAN": "🇹🇿", "TOG": "🇹🇬", "TUN": "🇹🇳", "UGA": "🇺🇬",
    "ZAM": "🇿🇲", "ZIM": "🇿🇼",
    # Asia / Oceania / Middle East
    "AFG": "🇦🇫", "AUS": "🇦🇺", "BHR": "🇧🇭", "BNG": "🇧🇩",
    "CHN": "🇨🇳", "FIJ": "🇫🇯", "IDN": "🇮🇩", "IND": "🇮🇳",
    "IRN": "🇮🇷", "IRQ": "🇮🇶", "JOR": "🇯🇴", "JPN": "🇯🇵",
    "KOR": "🇰🇷", "KSA": "🇸🇦", "KUW": "🇰🇼", "LBN": "🇱🇧",
    "MAS": "🇲🇾", "NZL": "🇳🇿", "OMA": "🇴🇲", "PAK": "🇵🇰",
    "PHI": "🇵🇭", "PRK": "🇰🇵", "QAT": "🇶🇦", "SGP": "🇸🇬",
    "SYR": "🇸🇾", "THA": "🇹🇭", "TJK": "🇹🇯", "TKM": "🇹🇲",
    "UAE": "🇦🇪", "UZB": "🇺🇿", "VIE": "🇻🇳", "YEM": "🇾🇪",
}


def _require_config() -> None:
    missing = []
    if not settings.football_api_base_url:
        missing.append("FOOTBALL_API_BASE_URL")
    if not settings.football_api_key:
        missing.append("FOOTBALL_API_KEY")
    if missing:
        raise FootballApiNotConfigured(
            f"Missing environment variable(s): {', '.join(missing)}. "
            "Configure them to enable external match synchronization."
        )


def _build_client() -> httpx.Client:
    return httpx.Client(
        base_url=settings.football_api_base_url.rstrip("/"),
        headers={"X-Auth-Token": settings.football_api_key},
        timeout=15.0,
    )


def _fetch_raw_matches(competition_id: str) -> list[dict[str, Any]]:
    with _build_client() as client:
        try:
            resp = client.get(f"/competitions/{competition_id}/matches")
            resp.raise_for_status()
        except httpx.TimeoutException as exc:
            raise FootballApiError("Request to football API timed out after 15 s") from exc
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:200]
            raise FootballApiError(
                f"Football API returned HTTP {exc.response.status_code}: {body}"
            ) from exc
        except httpx.RequestError as exc:
            raise FootballApiError(f"Network error reaching football API: {exc}") from exc

        try:
            return resp.json().get("matches", [])
        except Exception as exc:
            raise FootballApiError("Football API returned unparseable response") from exc


# TLAs que a API retorna de forma inconsistente — normaliza para o código canônico
_TLA_ALIAS: dict[str, str] = {
    "CUR": "CUW",  # Curaçao: API às vezes usa CUR, às vezes CUW
    "URU": "URY",  # Uruguai: API às vezes usa URU (FIFA), às vezes URY (ISO-3166)
}

_PT_NAME_MAP: dict[str, str] = {
    "ALG": "Argélia",
    "ARG": "Argentina",
    "AUS": "Austrália",
    "AUT": "Áustria",
    "BEL": "Bélgica",
    "BIH": "Bósnia e Herzegovina",
    "BRA": "Brasil",
    "CAN": "Canadá",
    "CIV": "Costa do Marfim",
    "COD": "RD Congo",
    "COL": "Colômbia",
    "CPV": "Cabo Verde",
    "CRO": "Croácia",
    "CUW": "Curaçao",
    "CZE": "República Tcheca",
    "ECU": "Equador",
    "EGY": "Egito",
    "ENG": "Inglaterra",
    "ESP": "Espanha",
    "FRA": "França",
    "GER": "Alemanha",
    "GHA": "Gana",
    "HAI": "Haiti",
    "IRN": "Irã",
    "IRQ": "Iraque",
    "JOR": "Jordânia",
    "JPN": "Japão",
    "KOR": "Coreia do Sul",
    "KSA": "Arábia Saudita",
    "MAR": "Marrocos",
    "MEX": "México",
    "NED": "Holanda",
    "NOR": "Noruega",
    "NZL": "Nova Zelândia",
    "PAN": "Panamá",
    "PAR": "Paraguai",
    "POR": "Portugal",
    "QAT": "Catar",
    "RSA": "África do Sul",
    "SCO": "Escócia",
    "SEN": "Senegal",
    "SUI": "Suíça",
    "SWE": "Suécia",
    "TUN": "Tunísia",
    "TUR": "Turquia",
    "URY": "Uruguai",
    "USA": "EUA",
    "UZB": "Uzbequistão",
}


def _map_phase(stage: str | None) -> MatchPhase:
    return _STAGE_MAP.get(stage or "", MatchPhase.group_stage)


def _map_status(status: str | None) -> MatchStatus:
    return _STATUS_MAP.get(status or "", MatchStatus.upcoming)


def _upsert_team(db: Session, raw_team: dict[str, Any]) -> Team | None:
    if not raw_team:
        return None

    tla: str = (raw_team.get("tla") or "").upper()
    tla = _TLA_ALIAS.get(tla, tla)
    api_name: str = raw_team.get("name") or raw_team.get("shortName") or ""
    if not tla or not api_name:
        return None

    pt_name = _PT_NAME_MAP.get(tla, api_name)

    team = db.scalar(select(Team).where(Team.code == tla))
    if team is None:
        team = Team(
            id=new_id(),
            name=pt_name,
            code=tla,
            flag=_FLAG_MAP.get(tla),
        )
        db.add(team)
        db.flush()
    else:
        team.name = pt_name
        if team.flag is None:
            team.flag = _FLAG_MAP.get(tla)
    return team


def _parse_kickoff(utc_date: str | None) -> datetime | None:
    if not utc_date:
        return None
    try:
        dt = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Public sync function
# ---------------------------------------------------------------------------

# Window used only to re-attach legacy rows synced before external_id existed
# (or duplicates from before the cleanup script ran) to the provider's raw id,
# instead of creating a new row when the provider reschedules kickoff_at.
_LEGACY_MATCH_LOOKUP_WINDOW = timedelta(hours=24)


def _find_existing_match(
    db: Session, *, external_id: str | None, home_team_id: str, away_team_id: str, kickoff: datetime
) -> Match | None:
    if external_id is not None:
        match = db.scalar(select(Match).where(Match.external_id == external_id))
        if match is not None:
            return match

    return db.scalar(
        select(Match).where(
            Match.home_team_id == home_team_id,
            Match.away_team_id == away_team_id,
            Match.external_id.is_(None),
            Match.kickoff_at >= kickoff - _LEGACY_MATCH_LOOKUP_WINDOW,
            Match.kickoff_at <= kickoff + _LEGACY_MATCH_LOOKUP_WINDOW,
        )
    )


def sync_matches(db: Session, competition_id: str = "2000") -> dict[str, int]:
    """Pull matches from the external API and upsert them into the database.

    Returns a dict with ``synced`` (created/updated) and ``skipped`` counts.
    Raises FootballApiNotConfigured or FootballApiError on failure.
    """
    _require_config()
    _check_and_set_cooldown()

    raw_matches = _fetch_raw_matches(competition_id)

    synced = 0
    skipped = 0

    for raw in raw_matches:
        try:
            kickoff = _parse_kickoff(raw.get("utcDate"))
            if kickoff is None:
                skipped += 1
                continue

            home_team = _upsert_team(db, raw.get("homeTeam") or {})
            away_team = _upsert_team(db, raw.get("awayTeam") or {})
            if home_team is None or away_team is None or home_team.id == away_team.id:
                skipped += 1
                continue

            phase = _map_phase(raw.get("stage"))
            ext_status = _map_status(raw.get("status"))

            # fullTime holds the definitive score for both regular-time and
            # extra-time/penalty matches once the provider settles it; halfTime
            # is interim and must never be used here.
            score_full = (raw.get("score") or {}).get("fullTime") or {}
            home_score: int | None = score_full.get("home")
            away_score: int | None = score_full.get("away")

            group_label: str | None = raw.get("group")
            venue: str = (raw.get("venue") or "A definir")[:255]

            raw_id = raw.get("id")
            external_id: str | None = str(raw_id) if raw_id is not None else None

            existing = _find_existing_match(
                db,
                external_id=external_id,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                kickoff=kickoff,
            )

            if existing is None:
                existing = Match(
                    id=new_id(),
                    external_id=external_id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    kickoff_at=kickoff,
                    venue=venue,
                    phase=phase.value,
                    world_cup_group=group_label,
                    status=ext_status.value,
                    home_score=home_score,
                    away_score=away_score,
                )
                db.add(existing)
            else:
                # Backfill external_id onto legacy/duplicate rows so future
                # syncs match on it directly instead of the fuzzy time window.
                if existing.external_id is None:
                    existing.external_id = external_id

                # A finished match can still receive corrected scores from the
                # provider (own-goal/VAR corrections), so finished->finished
                # updates are allowed. Only a real regression — provider
                # reporting upcoming/live for a match we already have as
                # finished — is rejected. A finished status without a score is
                # treated as a malformed payload and ignored, so it can't wipe
                # a previously-stored correct score.
                is_regression = (
                    existing.status == MatchStatus.finished.value and ext_status != MatchStatus.finished
                )
                finished_without_score = ext_status == MatchStatus.finished and (
                    home_score is None or away_score is None
                )
                if not is_regression and not finished_without_score:
                    existing.status = ext_status.value
                    existing.home_score = home_score
                    existing.away_score = away_score
                existing.kickoff_at = kickoff
                existing.venue = venue
                existing.phase = phase.value
                existing.world_cup_group = group_label

            synced += 1

        except Exception:  # noqa: BLE001 – skip bad rows, keep going
            skipped += 1
            continue

    db.flush()
    return {"synced": synced, "skipped": skipped}
