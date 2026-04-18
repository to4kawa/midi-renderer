from __future__ import annotations

from dataclasses import dataclass


class TimingParseError(ValueError):
    """Raised when bar:beat:tick parsing fails."""


@dataclass(frozen=True)
class Position:
    bar: int
    beat: int
    tick: int


def parse_bar_beat_tick(value: str) -> Position:
    parts = value.split(":")
    if len(parts) != 3:
        raise TimingParseError(f"Invalid position format: {value}")

    try:
        bar, beat, tick = (int(part) for part in parts)
    except ValueError as exc:
        raise TimingParseError(f"Position contains non-integer values: {value}") from exc

    if bar < 0 or beat < 0 or tick < 0:
        raise TimingParseError(f"Position must be non-negative: {value}")

    return Position(bar=bar, beat=beat, tick=tick)


def to_absolute_ticks(position: Position, beats_per_bar: int, ppq: int) -> int:
    return ((position.bar * beats_per_bar) + position.beat) * ppq + position.tick
