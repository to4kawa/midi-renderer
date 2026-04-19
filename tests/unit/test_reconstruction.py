from __future__ import annotations

from pathlib import Path

from midi_renderer.common.paths import reference_song_dir
from midi_renderer.reconstruct.run_reconstruction import run_reconstruction


ROOT = Path(__file__).resolve().parents[2]


def test_run_reconstruction_generates_trial_artifacts_with_reference_song(tmp_path: Path) -> None:
    analysis_path = ROOT / "intake" / "analysis" / "tmp_neko_funjatta_test_piano_120_20260419T031454Z_254d9253.analysis.json"
    result = run_reconstruction(
        analysis_json_path=analysis_path,
        reconstructed_root=tmp_path,
        reference_song_dir=reference_song_dir("neko_funjatta_test_piano_120"),
        with_comparison=True,
    )

    assert result.render_path.exists()
    assert result.meta_path.exists()
    assert result.comparison_path.exists()
    assert result.comparison_mode == "reference_song"

    comparison = result.comparison_path.read_text(encoding="utf-8")
    for key in [
        "target_analysis_path",
        "generated_render_path",
        "generated_meta_path",
        "comparison_mode",
        "compared_reference_path",
        "short_summary",
        "obvious_matches",
        "obvious_differences",
        "unresolved_items",
    ]:
        assert key in comparison


def test_run_reconstruction_generates_trial_artifacts_without_reference_song(tmp_path: Path) -> None:
    analysis_path = ROOT / "intake" / "analysis" / "tmp_doremi_piano_120_4_4_20260419T045156Z_dbedf0d8.analysis.json"
    result = run_reconstruction(
        analysis_json_path=analysis_path,
        reconstructed_root=tmp_path,
    )

    assert result.render_path.exists()
    assert result.meta_path.exists()
    assert result.comparison_path is None
    assert result.comparison_mode == "disabled"


def test_run_reconstruction_generates_optional_comparison_when_requested(tmp_path: Path) -> None:
    analysis_path = ROOT / "intake" / "analysis" / "tmp_doremi_piano_120_4_4_20260419T045156Z_dbedf0d8.analysis.json"
    result = run_reconstruction(
        analysis_json_path=analysis_path,
        reconstructed_root=tmp_path,
        with_comparison=True,
    )

    assert result.comparison_path is not None
    assert result.comparison_path.exists()
    assert result.comparison_mode == "unavailable"

    comparison = result.comparison_path.read_text(encoding="utf-8")
    assert "comparison_mode: unavailable" in comparison
    assert "compared_reference_path" not in comparison
