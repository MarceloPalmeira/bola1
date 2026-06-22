"""One-off maintenance script: merges duplicate Team/Match rows and corrects
a known bad score (Espanha x Arábia Saudita).

Two independent root causes are handled:
  * The external provider sometimes returns an alternate TLA for the same
    country (see football_api._TLA_ALIAS, e.g. CUR/CUW, URU/URY). Before the
    alias existed, each variant created its own Team row, which in turn made
    every fixture for that country get synced twice under two different
    team_ids — invisible to a dedup that only looks at exact team_id pairs.
  * The legacy sync upsert key (home/away team + exact kickoff_at, no
    external_id) created a new Match row whenever the provider reshuffled
    kickoff_at.

Safe to run more than once: it only acts on duplicates / wrong scores that
are still present, and never deletes a row before re-pointing whatever
references it (matches -> teams, predictions/activity_events -> matches).

Run from app/api with the project's virtualenv active:

    uv run python -m bola1_api.scripts.cleanup_duplicate_matches            # applies changes
    uv run python -m bola1_api.scripts.cleanup_duplicate_matches --dry-run  # preview only, rolls back

What it does, in order:
  1. Merges any legacy Team row created under a TLA alias into the
     canonical team, re-pointing the matches that referenced it.
  2. Groups matches by (home_team_id, away_team_id) and clusters rows whose
     kickoff_at falls within 48h of each other — the same real-world
     fixture synced more than once.
  3. For each cluster, keeps the most complete row (finished with a score >
     live > upcoming; ties broken by external_id present, a real venue,
     number of attached predictions, and finally the oldest row) and
     re-points predictions/activity events from the others onto it before
     deleting the duplicates. A user who predicted on more than one
     duplicate keeps only the prediction tied to the surviving match; the
     other is dropped (the unique user+group+match constraint forbids two),
     its activity trail re-pointed rather than deleted.
  4. Corrects the Espanha x Arábia Saudita match to 4-0 (Espanha) if it's
     present with a different score.
  5. Recalculates prediction points for every match touched by steps 3-4.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from bola1_api.db.session import SessionLocal
from bola1_api.models import ActivityEvent, Match, MatchStatus, Prediction, Team
from bola1_api.services.football_api import _TLA_ALIAS
from bola1_api.services.scoring import recalculate_match_points

_CLUSTER_WINDOW = timedelta(hours=48)

_STATUS_RANK = {
    MatchStatus.finished.value: 2,
    MatchStatus.live.value: 1,
    MatchStatus.upcoming.value: 0,
}

# (home_code, away_code, correct_home_score, correct_away_score)
_KNOWN_SCORE_FIXES: list[tuple[str, str, int, int]] = [
    ("ESP", "KSA", 4, 0),
]


def _merge_duplicate_teams(db: Session) -> list[dict]:
    """Folds legacy Team rows (created under a now-aliased TLA) into the
    canonical team, re-pointing any matches that reference them."""
    merges: list[dict] = []
    for wrong_code, correct_code in _TLA_ALIAS.items():
        wrong_team = db.scalar(select(Team).where(Team.code == wrong_code))
        if wrong_team is None:
            continue

        correct_team = db.scalar(select(Team).where(Team.code == correct_code))
        if correct_team is None:
            # No canonical row exists yet — just rename this one in place.
            wrong_team.code = correct_code
            merges.append({"from_code": wrong_code, "to_code": correct_code, "matches_repointed": 0})
            continue

        repointed = 0
        for match in list(db.scalars(select(Match).where(Match.home_team_id == wrong_team.id))):
            if match.away_team_id == correct_team.id:
                continue  # would violate ck_matches_distinct_teams; leave for manual review
            match.home_team_id = correct_team.id
            repointed += 1
        for match in list(db.scalars(select(Match).where(Match.away_team_id == wrong_team.id))):
            if match.home_team_id == correct_team.id:
                continue
            match.away_team_id = correct_team.id
            repointed += 1
        db.flush()

        still_referenced = db.scalar(
            select(Match).where((Match.home_team_id == wrong_team.id) | (Match.away_team_id == wrong_team.id))
        )
        if still_referenced is None:
            db.delete(wrong_team)
            db.flush()

        merges.append({"from_code": wrong_code, "to_code": correct_code, "matches_repointed": repointed})

    return merges


def _completeness_key(match: Match, prediction_counts: dict[str, int]) -> tuple:
    has_score = match.home_score is not None and match.away_score is not None
    return (
        _STATUS_RANK.get(match.status, 0),
        1 if has_score else 0,
        1 if match.external_id else 0,
        1 if match.venue and match.venue != "A definir" else 0,
        1 if match.world_cup_group else 0,
        prediction_counts.get(match.id, 0),
        -match.created_at.timestamp(),  # ties go to the older (more established) row
    )


def _cluster_matches(matches: list[Match]) -> list[list[Match]]:
    by_pair: dict[tuple[str, str], list[Match]] = defaultdict(list)
    for match in matches:
        by_pair[(match.home_team_id, match.away_team_id)].append(match)

    clusters: list[list[Match]] = []
    for pair_matches in by_pair.values():
        pair_matches.sort(key=lambda m: m.kickoff_at)
        current: list[Match] = []
        for match in pair_matches:
            if current and match.kickoff_at - current[-1].kickoff_at > _CLUSTER_WINDOW:
                clusters.append(current)
                current = []
            current.append(match)
        if current:
            clusters.append(current)

    return [cluster for cluster in clusters if len(cluster) > 1]


def _match_snapshot(match: Match, prediction_counts: dict[str, int], team_codes: dict[str, str]) -> dict:
    return {
        "id": match.id,
        "home": team_codes.get(match.home_team_id, match.home_team_id),
        "away": team_codes.get(match.away_team_id, match.away_team_id),
        "kickoff_at": match.kickoff_at.isoformat(),
        "status": match.status,
        "home_score": match.home_score,
        "away_score": match.away_score,
        "external_id": match.external_id,
        "predictions": prediction_counts.get(match.id, 0),
    }


def _repoint_match_references(db: Session, *, from_match: Match, to_match: Match) -> list[dict]:
    dropped_conflicts: list[dict] = []
    predictions = list(db.scalars(select(Prediction).where(Prediction.match_id == from_match.id)))
    for prediction in predictions:
        conflict = db.scalar(
            select(Prediction).where(
                Prediction.match_id == to_match.id,
                Prediction.group_id == prediction.group_id,
                Prediction.user_id == prediction.user_id,
            )
        )
        if conflict is not None:
            # User already has a prediction on the surviving match — the
            # unique (user, group, match) constraint forbids a second one.
            # Detach its activity trail instead of losing it, then drop it.
            dropped_conflicts.append(
                {
                    "user_id": prediction.user_id,
                    "group_id": prediction.group_id,
                    "dropped_match_id": from_match.id,
                    "dropped_score": [prediction.home_score, prediction.away_score],
                    "dropped_points": prediction.points,
                    "kept_match_id": to_match.id,
                    "kept_score": [conflict.home_score, conflict.away_score],
                    "kept_points": conflict.points,
                }
            )
            events = list(db.scalars(select(ActivityEvent).where(ActivityEvent.prediction_id == prediction.id)))
            for event in events:
                event.prediction_id = None
                event.match_id = to_match.id
            db.flush()
            db.delete(prediction)
        else:
            prediction.match_id = to_match.id
    db.flush()

    events = list(db.scalars(select(ActivityEvent).where(ActivityEvent.match_id == from_match.id)))
    for event in events:
        event.match_id = to_match.id
    db.flush()

    return dropped_conflicts


def _merge_cluster(db: Session, cluster: list[Match], prediction_counts: dict[str, int], team_codes: dict[str, str]) -> dict:
    ordered = sorted(cluster, key=lambda m: _completeness_key(m, prediction_counts), reverse=True)
    canonical, duplicates = ordered[0], ordered[1:]
    dropped_snapshots = [_match_snapshot(m, prediction_counts, team_codes) for m in duplicates]

    for dup in duplicates:
        if canonical.external_id is None and dup.external_id is not None:
            canonical.external_id = dup.external_id
        if canonical.status != MatchStatus.finished.value and dup.status == MatchStatus.finished.value:
            canonical.status = dup.status
            canonical.home_score = dup.home_score
            canonical.away_score = dup.away_score
        if canonical.venue == "A definir" and dup.venue and dup.venue != "A definir":
            canonical.venue = dup.venue
        if not canonical.world_cup_group and dup.world_cup_group:
            canonical.world_cup_group = dup.world_cup_group

    conflicts: list[dict] = []
    for dup in duplicates:
        conflicts.extend(_repoint_match_references(db, from_match=dup, to_match=canonical))
        db.delete(dup)
    db.flush()

    return {
        "canonical": _match_snapshot(canonical, prediction_counts, team_codes),
        "dropped": dropped_snapshots,
        "prediction_conflicts": conflicts,
    }


def _fix_known_bad_scores(db: Session) -> list[dict]:
    fixes: list[dict] = []
    for home_code, away_code, correct_home_score, correct_away_score in _KNOWN_SCORE_FIXES:
        home_team = db.scalar(select(Team).where(Team.code == home_code))
        away_team = db.scalar(select(Team).where(Team.code == away_code))
        if home_team is None or away_team is None:
            continue

        straight = list(
            db.scalars(select(Match).where(Match.home_team_id == home_team.id, Match.away_team_id == away_team.id))
        )
        flipped = list(
            db.scalars(select(Match).where(Match.home_team_id == away_team.id, Match.away_team_id == home_team.id))
        )

        for match in straight:
            target_home, target_away = correct_home_score, correct_away_score
            if match.home_score != target_home or match.away_score != target_away or match.status != MatchStatus.finished.value:
                fixes.append(
                    {
                        "match_id": match.id,
                        "before": [match.home_score, match.away_score, match.status],
                        "after": [target_home, target_away, MatchStatus.finished.value],
                    }
                )
                match.home_score, match.away_score, match.status = target_home, target_away, MatchStatus.finished.value

        target_home, target_away = correct_away_score, correct_home_score
        for match in flipped:
            if match.home_score != target_home or match.away_score != target_away or match.status != MatchStatus.finished.value:
                fixes.append(
                    {
                        "match_id": match.id,
                        "before": [match.home_score, match.away_score, match.status],
                        "after": [target_home, target_away, MatchStatus.finished.value],
                    }
                )
                match.home_score, match.away_score, match.status = target_home, target_away, MatchStatus.finished.value

    db.flush()
    return fixes


def cleanup(db: Session | None = None, *, dry_run: bool = False) -> dict[str, object]:
    owns_session = db is None
    db = db or SessionLocal()
    try:
        team_merges = _merge_duplicate_teams(db)

        matches = list(db.scalars(select(Match)))
        team_codes = {team.id: team.code for team in db.scalars(select(Team))}
        prediction_counts: dict[str, int] = defaultdict(int)
        for prediction in db.scalars(select(Prediction)):
            prediction_counts[prediction.match_id] += 1

        clusters = _cluster_matches(matches)
        cluster_reports = [_merge_cluster(db, cluster, prediction_counts, team_codes) for cluster in clusters]

        score_fixes = _fix_known_bad_scores(db)

        touched_ids = {report["canonical"]["id"] for report in cluster_reports}
        touched_ids.update(fix["match_id"] for fix in score_fixes)
        for match_id in touched_ids:
            match = db.get(Match, match_id)
            if match is not None and match.status == MatchStatus.finished.value:
                recalculate_match_points(db, match=match)

        result: dict[str, object] = {
            "dry_run": dry_run,
            "team_merges": team_merges,
            "duplicate_groups_merged": len(clusters),
            "matches_deleted": sum(len(cluster) - 1 for cluster in clusters),
            "scores_corrected": len(score_fixes),
            "clusters": cluster_reports,
            "score_fixes": score_fixes,
        }

        if dry_run:
            db.rollback()
        else:
            db.commit()

        return result
    finally:
        if owns_session:
            db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run every check and print what would change, but roll back instead of committing.",
    )
    args = parser.parse_args()

    outcome = cleanup(dry_run=args.dry_run)
    print(json.dumps(outcome, indent=2, default=str, ensure_ascii=False))
