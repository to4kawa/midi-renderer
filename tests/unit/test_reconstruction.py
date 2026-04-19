from __future__ import annotations

from pathlib import Path

from midi_renderer.common.paths import intake_reconstructed_dir, reference_neko_song_dir
from midi_renderer.reconstruct.run_reconstruction import run_reconstruction


ROOT = Path(__file__).resolve().parents[2]


def test_run_reconstruction_generates_trial_artifacts() -> None:
    analysis_path = ROOT / "intake" / "analysis" / "tmp_neko_funjatta_test_piano_120_20260419T031454Z_254d9253.analysis.json"
    result = run_reconstruction(
        analysis_json_path=analysis_path,
        reconstructed_root=intake_reconstructed_dir(),
        reference_song_dir=reference_neko_song_dir(),
    )

    assert result.render_path.exists()
    assert result.meta_path.exists()
    assert result.comparison_path.exists()

    comparison = result.comparison_path.read_text(encoding="utf-8")
    for key in [
        "compared_reference_path",
        "generated_render_path",
        "generated_meta_path",
        "short_summary",
        "obvious_matches",
        "obvious_differences",
        "unresolved_items",
    ]:
        assert key in comparison
