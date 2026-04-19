from __future__ import annotations

from pathlib import Path

from midi_renderer.analysis.midi_to_json import build_analysis_payload


ROOT = Path(__file__).resolve().parents[2]


def test_build_analysis_payload_includes_required_sections() -> None:
    midi_path = ROOT / "intake" / "midi" / "neko_funjatta_test_piano_120.mid"
    temporary_id, analysis_id, payload = build_analysis_payload(midi_path=midi_path, repository_root=ROOT)

    assert temporary_id.startswith("tmp_")
    assert analysis_id.startswith("analysis_tmp_")

    for key in [
        "schema_version",
        "analysis_id",
        "temporary_id",
        "source",
        "observed",
        "inferred",
        "unknown",
        "quality",
        "provenance",
    ]:
        assert key in payload

    observed = payload["observed"]
    for key in ["tempo_map", "time_signatures", "note_events", "total_ticks", "first_note_tick", "last_note_tick"]:
        assert key in observed
    first_note_event = observed["note_events"][0]
    assert "track_index" in first_note_event
    assert "pitch" in first_note_event
    assert "track" not in first_note_event
    assert "note" not in first_note_event

    assert payload["schema_version"] == "analysis.v0.1"
    assert payload["unknown"]["fields"]
    assert "deferred_fields" not in payload["unknown"]
    assert payload["quality"]["lossy_points"]
    assert payload["provenance"]["generator_version"] == "0.1.0"

    assert payload["source"]["original_filename"] == midi_path.name
    assert payload["source"]["track_count"] >= 1
    assert payload["observed"]["note_events"]
