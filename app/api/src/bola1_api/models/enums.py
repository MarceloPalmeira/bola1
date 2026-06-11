from enum import StrEnum


class GroupRole(StrEnum):
    admin = "admin"
    member = "member"


class MatchPhase(StrEnum):
    group_stage = "group-stage"
    round_of_16 = "round-of-16"
    quarter_finals = "quarter-finals"
    semi_finals = "semi-finals"
    final = "final"


class MatchStatus(StrEnum):
    upcoming = "upcoming"
    live = "live"
    finished = "finished"


class PredictionResultType(StrEnum):
    exact = "exact"
    winner = "winner"
    miss = "miss"


class ActivityEventType(StrEnum):
    join = "join"
    prediction = "prediction"
    result = "result"
