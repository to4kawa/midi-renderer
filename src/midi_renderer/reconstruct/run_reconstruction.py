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


@dataclass(frozen=True)
class ReconstructionResult:
    temporary_id: str
    output_dir: Path
    render_path: Path
    meta_path: Path
    comparison_path: Path


def _build_render(analysis: dict[str, Any], reference_song_ref: str) -> dict[str, Any]:
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
                "track": "piano",
                "pitch": int(event["pitch"]),
                "start": _tick_to_bar_beat_tick(int(event["start_tick"]), ppq, numerator),
                "duration": _duration_to_bar_beat_tick_delta(int(event["duration_ticks"]), ppq, numerator),
                "velocity": int(event.get("velocity", 96)),
            }
        )

    return {
        "schema_version": "0.1",
        "song_ref": reference_song_ref,
        "format": "bootstrap",
        "transport": {"bpm": bpm, "ppq": ppq, "time_signature": f"{numerator}/{denominator}"},
        "tracks": [
            {
                "id": "piano",
                "name": "Piano",
                "instrument": "Acoustic Grand Piano",
                "channel": 0,
                "program": 0,
            }
        ],
        "notes": notes,
    }


def _build_meta(analysis: dict[str, Any], reference_song_ref: str, analysis_path: Path) -> dict[str, Any]:
    inferred = analysis.get("inferred", {})
    unknown = analysis.get("unknown", {})
    quality = analysis.get("quality", {})
    return {
        "schema_version": "0.1",
        "song_ref": reference_song_ref,
        "title": inferred.get("provisional_title", "Provisional title"),
        "usage": "reconstruction trial artifact (not finalized)",
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


def _build_comparison(
    generated_render: dict[str, Any],
    generated_meta: dict[str, Any],
    generated_render_path: Path,
    generated_meta_path: Path,
    reference_render: dict[str, Any],
    reference_meta: dict[str, Any],
    compared_reference_path: str,
) -> str:
    generated_notes = generated_render.get("notes", [])
    reference_notes = reference_render.get("notes", [])

    obvious_matches: list[str] = []
    obvious_differences: list[str] = []

    if generated_render.get("transport") == reference_render.get("transport"):
        obvious_matches.append("transport fields match (bpm/ppq/time_signature)")
    else:
        obvious_differences.append("transport fields differ")

    if len(generated_notes) == len(reference_notes):
        obvious_matches.append(f"note count matches ({len(generated_notes)})")
    else:
        obvious_differences.append(
            f"note count differs (generated={len(generated_notes)}, reference={len(reference_notes)})"
        )

    if generated_notes[:5] == reference_notes[:5]:
        obvious_matches.append("first five note events match")
    else:
        obvious_differences.append("first five note events differ")

    title_match = generated_meta.get("title") == reference_meta.get("title")
    if title_match:
        obvious_matches.append("meta title matches reference")
    else:
        obvious_differences.append("meta title differs (provisional is acceptable)")

    unresolved_items = [
        "single-track piano hardcoded for first pass",
        "no finalize promotion to songs/",
        "no advanced semantic comparison scoring",
    ]

    short_summary = (
        "Minimal reconstruction produced trial render/meta artifacts and a fixed-reference comparison for neko case."
    )

    lines = [
        f"compared_reference_path: {compared_reference_path}",
        f"generated_render_path: {generated_render_path}",
        f"generated_meta_path: {generated_meta_path}",
        "",
        f"short_summary: {short_summary}",
        "",
        "obvious_matches:",
    ]
    lines.extend([f"- {item}" for item in obvious_matches] or ["- none"])
    lines.append("")
    lines.append("obvious_differences:")
    lines.extend([f"- {item}" for item in obvious_differences] or ["- none"])
    lines.append("")
    lines.append("unresolved_items:")
    lines.extend([f"- {item}" for item in unresolved_items])
    lines.append("")
    return "\n".join(lines)


def run_reconstruction(
    analysis_json_path: Path,
    reconstructed_root: Path,
    reference_song_dir: Path,
) -> ReconstructionResult:
    analysis = json.loads(analysis_json_path.read_text(encoding="utf-8"))
    temporary_id = str(analysis.get("temporary_id") or "tmp_unknown")
    output_dir = reconstructed_root / temporary_id
    output_dir.mkdir(parents=True, exist_ok=True)

    reference_render = json.loads(json.dumps({}))
    reference_meta = json.loads(json.dumps({}))
    try:
        import yaml  # type: ignore

        reference_render = yaml.safe_load((reference_song_dir / "render.yaml").read_text(encoding="utf-8"))
        reference_meta = yaml.safe_load((reference_song_dir / "meta.yaml").read_text(encoding="utf-8"))
    except ModuleNotFoundError:
        pass

    render = _build_render(analysis, reference_song_ref=reference_song_dir.name)
    meta = _build_meta(analysis, reference_song_ref=reference_song_dir.name, analysis_path=analysis_json_path)

    render_path = output_dir / "render.yaml"
    meta_path = output_dir / "meta.yaml"
    comparison_path = output_dir / "comparison.md"

    render_path.write_text(_dump_yaml(render), encoding="utf-8")
    meta_path.write_text(_dump_yaml(meta), encoding="utf-8")

    comparison = _build_comparison(
        generated_render=render,
        generated_meta=meta,
        generated_render_path=render_path,
        generated_meta_path=meta_path,
        reference_render=reference_render,
        reference_meta=reference_meta,
        compared_reference_path=str(reference_song_dir),
    )
    comparison_path.write_text(comparison, encoding="utf-8")

    return ReconstructionResult(
        temporary_id=temporary_id,
        output_dir=output_dir,
        render_path=render_path,
        meta_path=meta_path,
        comparison_path=comparison_path,
    )
