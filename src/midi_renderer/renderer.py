from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from midi_renderer.timing import parse_bar_beat_tick


@dataclass(frozen=True)
class MidiNoteEvent:
    tick: int
    type: str
    channel: int
    pitch: int
    velocity: int


@dataclass(frozen=True)
class MidiTrackRender:
    track_id: str
    name: str
    channel: int
    program: int
    events: list[MidiNoteEvent]


@dataclass(frozen=True)
class RenderResult:
    song_ref: str
    ppq: int
    bpm: float
    time_signature: tuple[int, int]
    tracks: list[MidiTrackRender]


def _parse_time_signature(value: Any) -> tuple[int, int]:
    if isinstance(value, str) and "/" in value:
        num_str, den_str = value.split("/", maxsplit=1)
        return int(num_str), int(den_str)
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return int(value[0]), int(value[1])
    raise ValueError(f"Invalid time signature: {value}")


def _position_to_ticks(start: str, beats_per_bar: int, ppq: int) -> int:
    pos = parse_bar_beat_tick(start)
    if pos.bar < 1 or pos.beat < 1:
        raise ValueError(f"start must be 1-based bar/beat: {start}")
    return (((pos.bar - 1) * beats_per_bar) + (pos.beat - 1)) * ppq + pos.tick


def _duration_to_ticks(duration: str, beats_per_bar: int, ppq: int) -> int:
    delta = parse_bar_beat_tick(duration)
    ticks = ((delta.bar * beats_per_bar) + delta.beat) * ppq + delta.tick
    return ticks if ticks > 0 else 1


def _clamp_midi_byte(value: Any, default: int) -> int:
    try:
        midi_value = int(value)
    except (TypeError, ValueError):
        return default
    return max(0, min(127, midi_value))


def render(spec: dict[str, Any]) -> RenderResult:
    transport = spec["transport"]
    bpm = float(transport["bpm"])
    ppq = int(transport["ppq"])
    time_signature = _parse_time_signature(transport["time_signature"])
    beats_per_bar = time_signature[0]

    rendered_tracks: dict[str, MidiTrackRender] = {}
    for track_spec in spec.get("tracks", []):
        if not isinstance(track_spec, dict):
            continue
        track_id = str(track_spec.get("id") or track_spec.get("name") or f"track_{len(rendered_tracks)}")
        rendered_tracks[track_id] = MidiTrackRender(
            track_id=track_id,
            name=str(track_spec.get("name", track_id)),
            channel=_clamp_midi_byte(track_spec.get("channel", 0), default=0),
            program=_clamp_midi_byte(track_spec.get("program", 0), default=0),
            events=[],
        )

    if not rendered_tracks:
        rendered_tracks["track_0"] = MidiTrackRender(
            track_id="track_0", name="Track 0", channel=0, program=0, events=[]
        )

    fallback_track_id = next(iter(rendered_tracks))

    for note in spec.get("notes", []):
        if not isinstance(note, dict):
            continue
        track_id = str(note.get("track", fallback_track_id))
        if track_id not in rendered_tracks:
            rendered_tracks[track_id] = MidiTrackRender(
                track_id=track_id,
                name=track_id,
                channel=0,
                program=0,
                events=[],
            )

        start_tick = _position_to_ticks(str(note["start"]), beats_per_bar, ppq)
        duration_ticks = _duration_to_ticks(str(note["duration"]), beats_per_bar, ppq)
        pitch = _clamp_midi_byte(note.get("pitch", 60), default=60)
        velocity = _clamp_midi_byte(note.get("velocity", 100), default=100)

        track = rendered_tracks[track_id]
        note_on = MidiNoteEvent(
            tick=start_tick,
            type="note_on",
            channel=track.channel,
            pitch=pitch,
            velocity=velocity,
        )
        note_off = MidiNoteEvent(
            tick=start_tick + duration_ticks,
            type="note_off",
            channel=track.channel,
            pitch=pitch,
            velocity=0,
        )
        track.events.extend([note_on, note_off])

    final_tracks: list[MidiTrackRender] = []
    for track in rendered_tracks.values():
        sorted_events = sorted(
            track.events,
            key=lambda event: (event.tick, 0 if event.type == "note_off" else 1, event.pitch),
        )
        final_tracks.append(
            MidiTrackRender(
                track_id=track.track_id,
                name=track.name,
                channel=track.channel,
                program=track.program,
                events=sorted_events,
            )
        )

    return RenderResult(
        song_ref=str(spec.get("song_ref", "unknown")),
        ppq=ppq,
        bpm=bpm,
        time_signature=time_signature,
        tracks=final_tracks,
    )
