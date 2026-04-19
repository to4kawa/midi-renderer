from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


def _tick_to_bar_beat_tick(absolute_tick: int, ppq: int, numerator: int) -> str:
    ticks_per_bar = ppq * numerator
    zero_based = max(0, absolute_tick)
    bar_index, bar_tick = divmod(zero_based, ticks_per_bar)
    beat_index, tick = divmod(bar_tick, ppq)
    return f"{bar_index + 1}:{beat_index + 1}:{tick}"


def _duration_to_bar_beat_tick_delta(duration_ticks: int, ppq: int, numerator: int) -> str:
    ticks_per_bar = ppq * numerator
    safe_duration = max(1, duration_ticks)
    bars, rem = divmod(safe_duration, ticks_per_bar)
    beats, tick = divmod(rem, ppq)
    return f"{bars}:{beats}:{tick}"


def _dump_yaml(data: dict[str, Any]) -> str:
    try:
        import yaml  # type: ignore

        return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    except ModuleNotFoundError:
        return json.dumps(data, ensure_ascii=False, indent=2)


def _load_structured_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        return loaded if isinstance(loaded, dict) else {}
    except ModuleNotFoundError:
        loaded = json.loads(text)
        return loaded if isinstance(loaded, dict) else {}


@dataclass(frozen=True)
class ReconstructionResult:
    temporary_id: str
    output_dir: Path
    render_path: Path
    meta_path: Path
    comparison_path: Path | None
    comparison_mode: str


def _build_render(analysis: dict[str, Any], song_ref: str, provisional_title: str) -> dict[str, Any]:
    if analysis.get("schema_version") != "analysis.v0.1":
        raise ValueError("Only schema_version=analysis.v0.1 is supported in this minimal reconstruction")

    source = analysis.get("source", {})
    observed = analysis.get("observed", {})
    note_events = observed.get("note_events", [])
    tempo_map = observed.get("tempo_map", [])
    time_signatures = observed.get("time_signatures", [])

    ppq = int(source.get("ticks_per_quarter") or 480)
    bpm = float(tempo_map[0].get("bpm", 120)) if tempo_map else 120

    numerator = 4
    denominator = 4
    if time_signatures:
        numerator = int(time_signatures[0].get("numerator", 4))
        denominator = int(time_signatures[0].get("denominator", 4))

    notes: list[dict[str, Any]] = []
    for event in note_events:
        notes.append(
            {
                "track": "primary",
                "pitch": int(event["pitch"]),
                "start": _tick_to_bar_beat_tick(int(event["start_tick"]), ppq, numerator),
                "duration": _duration_to_bar_beat_tick_delta(int(event["duration_ticks"]), ppq, numerator),
                "velocity": int(event.get("velocity", 96)),
            }
        )

    first_event = note_events[0] if note_events else {}
    channel = int(first_event.get("channel", 0))
    track_index = int(first_event.get("track_index", 0))

    return {
        "schema_version": "render.v0.1",
        "song_ref": song_ref,
        "title": provisional_title,
        "format": "bootstrap",
        "transport": {"bpm": bpm, "ppq": ppq, "time_signature": f"{numerator}/{denominator}"},
        "tracks": [
            {
                "id": "primary",
                "name": "Primary Track",
                "instrument": "unknown_or_assumed",
                "channel": channel,
                "source_track_index": track_index,
            }
        ],
        "notes": notes,
    }


def _build_meta(analysis: dict[str, Any], song_ref: str, analysis_path: Path) -> dict[str, Any]:
    inferred = analysis.get("inferred", {})
    unknown = analysis.get("unknown", {})
    quality = analysis.get("quality", {})
    return {
        "schema_version": "0.1",
        "song_ref": song_ref,
        "title": inferred.get("provisional_title", "Provisional title"),
        "usage": "bootstrap reconstruction artifact (observed-faithful, not finalized)",
        "source_request": {
            "analysis_json": str(analysis_path),
            "schema_version": analysis.get("schema_version"),
            "source_of_truth": "observed",
        },
        "review": {
            "status": "provisional",
            "unknown_fields": unknown.get("fields", []),
            "warnings": quality.get("warnings", []),
            "lossy_points": quality.get("lossy_points", []),
        },
    }


def _compare_reference_song(
    generated_render: dict[str, Any],
    generated_meta: dict[str, Any],
    reference_render: dict[str, Any],
    reference_meta: dict[str, Any],
) -> tuple[list[str], list[str]]:
    generated_notes = generated_render.get("notes", [])
    reference_notes = reference_render.get("notes", [])

    obvious_matches: list[str] = []
    obvious_differences: list[str] = []

    if generated_render.get("transport") == reference_render.get("transport"):
        obvious_matches.append("reference_song: transport fields match (bpm/ppq/time_signature)")
    else:
        obvious_differences.append("reference_song: transport fields differ")

    if len(generated_notes) == len(reference_notes):
        obvious_matches.append(f"reference_song: note count matches ({len(generated_notes)})")
    else:
        obvious_differences.append(
            f"reference_song: note count differs (generated={len(generated_notes)}, reference={len(reference_notes)})"
        )

    if generated_notes[:5] == reference_notes[:5]:
        obvious_matches.append("reference_song: first five note events match")
    else:
        obvious_differences.append("reference_song: first five note events differ")

    if generated_meta.get("title") == reference_meta.get("title"):
        obvious_matches.append("reference_song: meta title matches reference")
    else:
        obvious_differences.append("reference_song: meta title differs (provisional is acceptable)")

    return obvious_matches, obvious_differences


def _compare_song_intent(
    generated_render: dict[str, Any],
    generated_meta: dict[str, Any],
    song_intent: dict[str, Any],
) -> tuple[list[str], list[str]]:
    intent = song_intent.get("song_intent", song_intent)
    if not isinstance(intent, dict):
        return [], ["song_intent: input was not a mapping"]

    obvious_matches: list[str] = []
    obvious_differences: list[str] = []
    transport = generated_render.get("transport", {})

    intended_bpm = intent.get("intended_tempo_bpm")
    if isinstance(intended_bpm, (int, float)):
        generated_bpm = transport.get("bpm")
        if isinstance(generated_bpm, (int, float)) and abs(float(generated_bpm) - float(intended_bpm)) <= 3.0:
            obvious_matches.append(f"song_intent: tempo is close to intended ({generated_bpm} vs {intended_bpm})")
        else:
            obvious_differences.append(f"song_intent: tempo differs ({generated_bpm} vs {intended_bpm})")

    intended_meter = intent.get("intended_time_signature")
    if isinstance(intended_meter, str):
        generated_meter = str(transport.get("time_signature"))
        if generated_meter == intended_meter:
            obvious_matches.append(f"song_intent: meter matches intended ({intended_meter})")
        else:
            obvious_differences.append(f"song_intent: meter differs ({generated_meter} vs {intended_meter})")

    intended_bars = intent.get("intended_length_bars")
    if isinstance(intended_bars, int):
        notes = generated_render.get("notes", [])
        last_start_bar = 0
        for note in notes:
            try:
                bar_idx = int(str(note.get("start", "1:1:0")).split(":")[0])
                last_start_bar = max(last_start_bar, bar_idx)
            except (ValueError, IndexError):
                continue
        if last_start_bar == intended_bars:
            obvious_matches.append(f"song_intent: phrase length matches intended bars ({intended_bars})")
        else:
            obvious_differences.append(
                f"song_intent: phrase length likely differs (observed last-start-bar={last_start_bar}, intended={intended_bars})"
            )

    if intent.get("right_hand_intent"):
        obvious_matches.append("song_intent: right-hand melody intent acknowledged in comparison")
    if intent.get("left_hand_intent"):
        obvious_matches.append("song_intent: left-hand accompaniment intent acknowledged in comparison")

    timing_policy = str(intent.get("timing_policy", "")).lower()
    if "acceptable" in timing_policy or "allow" in timing_policy:
        obvious_matches.append("song_intent: timing deviations treated as acceptable per timing_policy")

    instrument_policy = str(intent.get("instrument_policy", "")).lower()
    if "not strict" in instrument_policy:
        obvious_matches.append("song_intent: instrument strictness relaxed per intent policy")

    provisional_title = str(generated_meta.get("title", ""))
    intent_title = intent.get("title")
    if isinstance(intent_title, str) and provisional_title and provisional_title != intent_title:
        obvious_differences.append("song_intent: title differs from intent title (allowed in provisional phase)")

    return obvious_matches, obvious_differences


def _build_comparison(
    target_analysis_path: Path,
    generated_render: dict[str, Any],
    generated_meta: dict[str, Any],
    generated_render_path: Path,
    generated_meta_path: Path,
    reference_render: dict[str, Any] | None,
    reference_meta: dict[str, Any] | None,
    compared_reference_path: str | None,
    song_intent: dict[str, Any] | None,
    used_song_intent_path: str | None,
) -> tuple[str, str]:
    has_reference = reference_render is not None and reference_meta is not None and compared_reference_path is not None
    has_intent = song_intent is not None and used_song_intent_path is not None

    if has_reference and has_intent:
        comparison_mode = "reference_song+song_intent"
    elif has_reference:
        comparison_mode = "reference_song"
    elif has_intent:
        comparison_mode = "song_intent"
    else:
        comparison_mode = "unavailable"

    obvious_matches: list[str] = []
    obvious_differences: list[str] = []

    if has_reference:
        m, d = _compare_reference_song(generated_render, generated_meta, reference_render or {}, reference_meta or {})
        obvious_matches.extend(m)
        obvious_differences.extend(d)

    if has_intent:
        m, d = _compare_song_intent(generated_render, generated_meta, song_intent or {})
        obvious_matches.extend(m)
        obvious_differences.extend(d)

    if comparison_mode == "unavailable":
        obvious_differences.append("no reference song and no song_intent were provided")

    unresolved_items = [
        "no finalize promotion to songs/",
        "no advanced semantic comparison scoring",
        "multi-instrument inference remains intentionally minimal",
    ]

    short_summary = "Generated reconstruction artifacts with intent-aware comparison fallback when canonical reference is absent."

    lines = [
        f"target_analysis_path: {target_analysis_path}",
        f"generated_render_path: {generated_render_path}",
        f"generated_meta_path: {generated_meta_path}",
        f"comparison_mode: {comparison_mode}",
    ]
    if compared_reference_path:
        lines.append(f"compared_reference_path: {compared_reference_path}")
    if used_song_intent_path:
        lines.append(f"used_song_intent_path: {used_song_intent_path}")
    lines.extend(
        [
            "",
            f"short_summary: {short_summary}",
            "",
            "obvious_matches:",
        ]
    )
    lines.extend([f"- {item}" for item in obvious_matches] or ["- none"])
    lines.append("")
    lines.append("obvious_differences:")
    lines.extend([f"- {item}" for item in obvious_differences] or ["- none"])
    lines.append("")
    lines.append("unresolved_items:")
    lines.extend([f"- {item}" for item in unresolved_items])
    lines.append("")
    return "\n".join(lines), comparison_mode


def run_reconstruction(
    analysis_json_path: Path,
    reconstructed_root: Path,
    reference_song_dir: Path | None = None,
    song_intent_path: Path | None = None,
    with_comparison: bool = False,
) -> ReconstructionResult:
    analysis = json.loads(analysis_json_path.read_text(encoding="utf-8"))
    temporary_id = str(analysis.get("temporary_id") or "tmp_unknown")
    output_dir = reconstructed_root / temporary_id
    output_dir.mkdir(parents=True, exist_ok=True)

    song_ref = temporary_id

    reference_render: dict[str, Any] | None = None
    reference_meta: dict[str, Any] | None = None
    compared_reference_path: str | None = None
    if reference_song_dir is not None:
        render_path = reference_song_dir / "render.yaml"
        meta_path = reference_song_dir / "meta.yaml"
        if render_path.exists() and meta_path.exists():
            reference_render = _load_structured_file(render_path)
            reference_meta = _load_structured_file(meta_path)
            compared_reference_path = str(reference_song_dir)

    song_intent: dict[str, Any] | None = None
    used_song_intent_path: str | None = None
    if song_intent_path is not None and song_intent_path.exists():
        song_intent = _load_structured_file(song_intent_path)
        used_song_intent_path = str(song_intent_path)

    provisional_title = str(analysis.get("inferred", {}).get("provisional_title") or "Provisional title")
    render = _build_render(analysis, song_ref=song_ref, provisional_title=provisional_title)
    meta = _build_meta(analysis, song_ref=song_ref, analysis_path=analysis_json_path)

    render_path = output_dir / "render.yaml"
    meta_path = output_dir / "meta.yaml"
    comparison_path = output_dir / "comparison.md"
    comparison_mode = "disabled"

    render_path.write_text(_dump_yaml(render), encoding="utf-8")
    meta_path.write_text(_dump_yaml(meta), encoding="utf-8")

    if with_comparison:
        comparison, comparison_mode = _build_comparison(
            target_analysis_path=analysis_json_path,
            generated_render=render,
            generated_meta=meta,
            generated_render_path=render_path,
            generated_meta_path=meta_path,
            reference_render=reference_render,
            reference_meta=reference_meta,
            compared_reference_path=compared_reference_path,
            song_intent=song_intent,
            used_song_intent_path=used_song_intent_path,
        )
        comparison_path.write_text(comparison, encoding="utf-8")
    else:
        comparison_path = None

    return ReconstructionResult(
        temporary_id=temporary_id,
        output_dir=output_dir,
        render_path=render_path,
        meta_path=meta_path,
        comparison_path=comparison_path,
        comparison_mode=comparison_mode,
    )
