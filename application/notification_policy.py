# application/notification_policy.py
"""
P1-F: tournament-level notification preferences.

Per-tournament JSON on TournamentModel.notification_prefs, e.g.
{"ROUND_CREATED": false} — an ABSENT key defaults to ENABLED, matching
the user-level channel-preference convention. These gates are consulted
at emission sites IN ADDITION to each recipient's own channel prefs.
"""
import json


# Event classes an organizer can toggle per tournament. Only types that
# actually have an emission site today are listed here.
TOURNAMENT_EVENT_TYPES = ("ROUND_CREATED", "TOURNAMENT_ANNOUNCEMENT")


def load_tournament_prefs(raw) -> dict:
    """Tolerant parse: junk payloads behave as all-enabled."""
    if not raw:
        return {}
    try:
        data = json.loads(raw) if isinstance(raw, str) else dict(raw)
    except (ValueError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def tournament_allows(raw, event_type: str) -> bool:
    prefs = load_tournament_prefs(raw)
    value = prefs.get(event_type)
    return True if value is None else bool(value)


def serialize_tournament_prefs(prefs: dict) -> str:
    clean = {
        k: bool(v) for k, v in (prefs or {}).items()
        if k in TOURNAMENT_EVENT_TYPES
    }
    return json.dumps(clean, ensure_ascii=False)
