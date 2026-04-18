from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RenderResult:
    song_ref: str
    event_count: int
    payload: dict[str, Any]


def render(spec: dict[str, Any]) -> RenderResult:
    """Bootstrap orchestration placeholder.

    In this stage, we only echo minimal render metadata.
    """
    song_ref = str(spec.get("song_ref", "unknown"))
    notes = spec.get("notes", [])
    event_count = len(notes) if isinstance(notes, list) else 0

    payload = {
        "format": spec.get("format"),
        "transport": spec.get("transport"),
        "tracks": spec.get("tracks"),
    }
    return RenderResult(song_ref=song_ref, event_count=event_count, payload=payload)
