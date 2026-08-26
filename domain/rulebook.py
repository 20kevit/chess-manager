# domain/rulebook.py
"""
Pure rulebook-domain primitives (P1-D).

Single source of truth for the structured-section JSON representation:
a list of {"key": str, "title": str, "body": str} objects, where list
order IS the display order. The vocabulary below is maintained (keys are
stable identifiers; titles are editable Persian defaults). No framework
imports allowed.
"""
import json
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Section:
    key: str
    title: str
    body: str


# Maintained predefined vocabulary for common tournament-rule sections.
# Keys are stable; organizers may edit titles/bodies freely and may add
# custom keys of their own ('other' covers free-form extras).
SECTION_VOCABULARY = [
    ("registration", "ثبت‌نام"),
    ("tournament_system", "نظام مسابقات"),
    ("schedule", "برنامه زمانی"),
    ("time_control", "کنترل زمان"),
    ("pairing", "جفت‌گذاری"),
    ("tie_breaks", "تای‌بریک‌ها"),
    ("player_obligations", "تعهدات بازیکنان"),
    ("withdrawal", "انصراف"),
    ("appeals", "شکایات و اعتراضات"),
    ("prizes", "جوایز"),
    ("other", "سایر"),
]

VOCABULARY_KEYS = {key for key, _ in SECTION_VOCABULARY}
DEFAULT_TITLES = dict(SECTION_VOCABULARY)


def default_title(key: str) -> str:
    """Persian default title for a known key; the key itself otherwise."""
    return DEFAULT_TITLES.get(key, key)


def parse_sections(raw) -> List[Section]:
    """Parse stored/posted sections JSON into ordered Sections.

    Tolerant by design: junk payloads parse to an empty list; entries
    that are not dicts or lack content are dropped silently so a bad
    edit can never break the public page.
    """
    if not raw:
        return []
    try:
        data = json.loads(raw) if isinstance(raw, str) else list(raw)
    except (ValueError, TypeError):
        return []
    if not isinstance(data, list):
        return []

    sections: List[Section] = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("key", "")).strip()
        title = str(entry.get("title", "")).strip()
        body = str(entry.get("body", "")).strip()
        if not key and not title and not body:
            continue
        sections.append(Section(
            key=key or "other",
            title=title or default_title(key),
            body=body,
        ))
    return sections


def serialize_sections(sections: List[Section]) -> str:
    """Canonical JSON text (list order preserved)."""
    return json.dumps(
        [{"key": s.key, "title": s.title, "body": s.body} for s in sections],
        ensure_ascii=False,
    )
