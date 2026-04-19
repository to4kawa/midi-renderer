from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import uuid

SCHEMA_VERSION = "analysis.v0.1"
GENERATOR_VERSION = "0.1.0"


@dataclass(frozen=True)
class AnalysisResult:
    temporary_id: str
    analysis_id: str
    output_path: Path
    payload: dict


class MidiParseError(ValueError):
    """Raised when a MIDI file cannot be parsed by the minimal parser."""


class _ByteReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def read(self, size: int) -> bytes:
        if self.pos + size > len(self.data):
            raise MidiParseError("Unexpected end-of-file while parsing MIDI")
        out = self.data[self.pos : self.pos + size]
        self.pos += size
        return out

    def read_u8(self) -> int:
        return self.read(1)[0]

    def read_u16(self) -> int:
        return int.from_bytes(self.read(2), "big")

    def read_u32(self) -> int:
        return int.from_bytes(self.read(4), "big")

    def read_varlen(self) -> int:
        value = 0
        for _ in range(4):
            byte = self.read_u8()
            value = (value << 7) | (byte & 0x7F)
            if (byte & 0x80) == 0:
                return value
        raise MidiParseError("Invalid variable-length quantity in MIDI stream")


@dataclass(frozen=True)
class ParsedMidi:
    midi_format: int
    ticks_per_quarter: int
    track_count: int
    observed: dict


def _slugify_filename(path: Path) -> str:
    stem = path.stem.lower()
    safe = "".join(ch if ch.isalnum() else "_" for ch in stem).strip("_")
    return safe or "untitled"


def _to_relative(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path.resolve())


def _build_ids(source_path: Path) -> tuple[str, str, str]:
    now = datetime.now(tz=timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    nonce = uuid.uuid4().hex[:8]
    base = _slugify_filename(source_path)
    temporary_id = f"tmp_{base}_{stamp}_{nonce}"
    analysis_id = f"analysis_{temporary_id}"
    generated_at = now.isoformat().replace("+00:00", "Z")
    return temporary_id, analysis_id, generated_at


def _microseconds_per_quarter_to_bpm(value: int) -> float:
    return round(60_000_000 / value, 6) if value > 0 else 0.0


def _parse_track(track_bytes: bytes, track_index: int) -> tuple[list[dict], list[dict], list[dict], int]:
    reader = _ByteReader(track_bytes)
    tempo_map: list[dict] = []
    time_signatures: list[dict] = []
    note_events: list[dict] = []

    absolute_tick = 0
    running_status: int | None = None
    active_notes: dict[tuple[int, int], list[tuple[int, int]]] = {}

    while reader.pos < len(track_bytes):
        delta = reader.read_varlen()
        absolute_tick += delta

        event_head = reader.read_u8()
        if event_head < 0x80:
            if running_status is None:
                raise MidiParseError("Running status encountered before any status byte")
            status = running_status
            data_start = event_head
        else:
            status = event_head
            data_start = None
            if status < 0xF0:
                running_status = status

        if status == 0xFF:
            meta_type = reader.read_u8()
            length = reader.read_varlen()
            payload = reader.read(length)

            if meta_type == 0x51 and length == 3:
                tempo = int.from_bytes(payload, "big")
                tempo_map.append(
                    {
                        "tick": absolute_tick,
                        "tempo_microseconds_per_quarter": tempo,
                        "bpm": _microseconds_per_quarter_to_bpm(tempo),
                        "track": track_index,
                    }
                )
            elif meta_type == 0x58 and length >= 2:
                numerator = payload[0]
                denominator = 2 ** payload[1]
                time_signatures.append(
                    {
                        "tick": absolute_tick,
                        "numerator": numerator,
                        "denominator": denominator,
                        "track": track_index,
                    }
                )
            continue

        if status in {0xF0, 0xF7}:
            length = reader.read_varlen()
            reader.read(length)
            continue

        event_type = status & 0xF0
        channel = status & 0x0F

        if event_type in {0xC0, 0xD0}:
            if data_start is None:
                reader.read_u8()
            continue

        if data_start is None:
            first_data = reader.read_u8()
        else:
            first_data = data_start
        second_data = reader.read_u8()

        if event_type == 0x90 and second_data > 0:
            key = (channel, first_data)
            active_notes.setdefault(key, []).append((absolute_tick, second_data))
            continue

        is_note_off = event_type == 0x80 or (event_type == 0x90 and second_data == 0)
        if not is_note_off:
            continue

        key = (channel, first_data)
        if key not in active_notes or not active_notes[key]:
            continue
        start_tick, velocity = active_notes[key].pop(0)
        end_tick = absolute_tick
        note_events.append(
            {
                "track_index": track_index,
                "channel": channel,
                "pitch": first_data,
                "start_tick": start_tick,
                "end_tick": end_tick,
                "duration_ticks": max(1, end_tick - start_tick),
                "velocity": velocity,
            }
        )

    return tempo_map, time_signatures, note_events, absolute_tick


def parse_midi_file(path: Path) -> ParsedMidi:
    reader = _ByteReader(path.read_bytes())
    if reader.read(4) != b"MThd":
        raise MidiParseError("Invalid MIDI header chunk")

    header_length = reader.read_u32()
    header_data = _ByteReader(reader.read(header_length))
    midi_format = header_data.read_u16()
    track_count = header_data.read_u16()
    division = header_data.read_u16()

    if division & 0x8000:
        raise MidiParseError("SMPTE time division is not supported in this minimal parser")
    ticks_per_quarter = division

    tempo_map: list[dict] = []
    time_signatures: list[dict] = []
    note_events: list[dict] = []
    total_ticks = 0

    for track_index in range(track_count):
        if reader.read(4) != b"MTrk":
            raise MidiParseError(f"Track {track_index} is missing MTrk marker")
        track_length = reader.read_u32()
        track_bytes = reader.read(track_length)

        t_map, t_sig, notes, track_ticks = _parse_track(track_bytes, track_index)
        tempo_map.extend(t_map)
        time_signatures.extend(t_sig)
        note_events.extend(notes)
        total_ticks = max(total_ticks, track_ticks)

    tempo_map.sort(key=lambda item: (item["tick"], item["track"]))
    time_signatures.sort(key=lambda item: (item["tick"], item["track"]))
    note_events.sort(key=lambda item: (item["start_tick"], item["track_index"], item["pitch"]))

    first_note_tick = min((event["start_tick"] for event in note_events), default=None)
    last_note_tick = max((event["end_tick"] for event in note_events), default=None)

    observed = {
        "tempo_map": tempo_map,
        "time_signatures": time_signatures,
        "note_events": note_events,
        "total_ticks": total_ticks,
        "first_note_tick": first_note_tick,
        "last_note_tick": last_note_tick,
    }

    return ParsedMidi(
        midi_format=midi_format,
        ticks_per_quarter=ticks_per_quarter,
        track_count=track_count,
        observed=observed,
    )


def _infer_fields(observed: dict, source_path: Path) -> dict:
    tempo_map = observed["tempo_map"]
    first_bpm = tempo_map[0]["bpm"] if tempo_map else None

    return {
        "provisional_title": source_path.stem,
        "tempo_summary": {
            "initial_bpm": first_bpm,
            "tempo_change_count": max(0, len(tempo_map) - 1),
            "has_explicit_tempo": bool(tempo_map),
        },
        "structural_summary": {
            "note_count": len(observed["note_events"]),
            "time_signature_change_count": max(0, len(observed["time_signatures"]) - 1),
            "track_count_with_notes": len({event["track_index"] for event in observed["note_events"]}),
        },
        "reconstruction_hints": {
            "preferred_quantization": "defer",
            "needs_manual_title_review": True,
            "notes": [
                "Provisional output intended for reverse-analysis iteration.",
                "Use observed.note_events as source-of-truth extraction output.",
            ],
        },
    }


def build_analysis_payload(midi_path: Path, repository_root: Path) -> tuple[str, str, dict]:
    parsed = parse_midi_file(midi_path)
    temporary_id, analysis_id, generated_at = _build_ids(midi_path)

    payload = {
        "schema_version": SCHEMA_VERSION,
        "analysis_id": analysis_id,
        "temporary_id": temporary_id,
        "source": {
            "original_filename": midi_path.name,
            "original_path": _to_relative(midi_path, repository_root),
            "midi_format": parsed.midi_format,
            "track_count": parsed.track_count,
            "ticks_per_quarter": parsed.ticks_per_quarter,
        },
        "observed": parsed.observed,
        "inferred": _infer_fields(parsed.observed, midi_path),
        "unknown": {
            "fields": [
                "final_song_id",
                "arrangement_sections",
                "render_yaml_mapping",
                "meta_yaml_mapping",
            ]
        },
        "quality": {
            "status": "provisional",
            "warnings": [
                "No advanced multi-instrument semantic inference.",
                "No cleanup/finalize integration in this step.",
            ],
            "lossy_points": [
                "instrument semantics not preserved",
                "section labels not recoverable from MIDI alone",
                "render/meta mapping not finalized",
            ],
        },
        "provenance": {
            "generated_at_utc": generated_at,
            "generator": "midi_renderer.analysis.midi_to_json",
            "generator_version": GENERATOR_VERSION,
            "mode": "single_file_minimal",
        },
    }
    return temporary_id, analysis_id, payload


def write_analysis_json(midi_path: Path, output_dir: Path, repository_root: Path) -> AnalysisResult:
    import json

    temporary_id, analysis_id, payload = build_analysis_payload(midi_path, repository_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{temporary_id}.analysis.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return AnalysisResult(
        temporary_id=temporary_id,
        analysis_id=analysis_id,
        output_path=output_path,
        payload=payload,
    )
