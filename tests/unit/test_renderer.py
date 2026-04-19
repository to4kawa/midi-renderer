from midi_renderer.renderer import render


def test_render_creates_note_events_from_bar_beat_tick() -> None:
    spec = {
        "song_ref": "song",
        "transport": {"bpm": 120, "ppq": 480, "time_signature": "3/4"},
        "tracks": [{"id": "piano", "channel": 0, "program": 0}],
        "notes": [
            {
                "track": "piano",
                "pitch": 67,
                "start": "1:1:0",
                "duration": "0:1:0",
                "velocity": 96,
            }
        ],
    }

    result = render(spec)

    assert result.ppq == 480
    assert result.time_signature == (3, 4)
    assert len(result.tracks) == 1
    assert [event.tick for event in result.tracks[0].events] == [0, 480]
