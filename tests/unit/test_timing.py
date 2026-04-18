import pytest

from midi_renderer.timing import Position, TimingParseError, parse_bar_beat_tick


def test_parse_bar_beat_tick_valid() -> None:
    result = parse_bar_beat_tick("1:2:120")

    assert result == Position(bar=1, beat=2, tick=120)


def test_parse_bar_beat_tick_invalid() -> None:
    with pytest.raises(TimingParseError):
        parse_bar_beat_tick("1:2")
