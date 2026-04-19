from __future__ import annotations

import math
from pathlib import Path

from midi_renderer.renderer import MidiTrackRender, RenderResult


def _u16(value: int) -> bytes:
    return int(value).to_bytes(2, byteorder="big", signed=False)


def _u32(value: int) -> bytes:
    return int(value).to_bytes(4, byteorder="big", signed=False)


def _var_len(value: int) -> bytes:
    if value < 0:
        raise ValueError("Variable-length quantity must be non-negative")

    encoded = bytearray([value & 0x7F])
    value >>= 7
    while value:
        encoded.insert(0, 0x80 | (value & 0x7F))
        value >>= 7
    return bytes(encoded)


def _chunk(chunk_type: bytes, payload: bytes) -> bytes:
    return chunk_type + _u32(len(payload)) + payload


def _meta_event(delta: int, meta_type: int, data: bytes) -> bytes:
    return _var_len(delta) + bytes([0xFF, meta_type]) + _var_len(len(data)) + data


def _build_conductor_track(result: RenderResult) -> bytes:
    numerator, denominator = result.time_signature
    midi_denominator = int(math.log2(denominator))
    tempo_us_per_quarter = int(round(60_000_000 / result.bpm))

    payload = bytearray()
    payload.extend(_meta_event(0, 0x51, tempo_us_per_quarter.to_bytes(3, byteorder="big")))
    payload.extend(_meta_event(0, 0x58, bytes([numerator, midi_denominator, 24, 8])))
    payload.extend(_meta_event(0, 0x2F, b""))
    return _chunk(b"MTrk", bytes(payload))


def _text_event(delta: int, text: str) -> bytes:
    encoded = text.encode("utf-8")
    return _meta_event(delta, 0x03, encoded)


def _build_note_track(track: MidiTrackRender) -> bytes:
    payload = bytearray()
    payload.extend(_text_event(0, track.name))
    payload.extend(_var_len(0) + bytes([0xC0 | track.channel, track.program]))

    last_tick = 0
    for event in track.events:
        delta = max(0, event.tick - last_tick)
        status = (0x90 if event.type == "note_on" else 0x80) | event.channel
        payload.extend(_var_len(delta) + bytes([status, event.pitch, event.velocity]))
        last_tick = event.tick

    payload.extend(_meta_event(0, 0x2F, b""))
    return _chunk(b"MTrk", bytes(payload))


def write_midi_output(result: RenderResult, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    tracks = [_build_conductor_track(result)]
    tracks.extend(_build_note_track(track) for track in result.tracks)

    header_payload = _u16(1) + _u16(len(tracks)) + _u16(result.ppq)
    midi_bytes = _chunk(b"MThd", header_payload) + b"".join(tracks)
    output.write_bytes(midi_bytes)
    return output
