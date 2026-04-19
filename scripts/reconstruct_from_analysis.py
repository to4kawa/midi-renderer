#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from midi_renderer.common.paths import intake_analysis_dir, intake_reconstructed_dir, reference_song_dir
from midi_renderer.reconstruct.run_reconstruction import run_reconstruction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reconstruct trial render/meta from analysis JSON")
    parser.add_argument(
        "analysis_json_path",
        nargs="?",
        help="Path to analysis.v0.1 JSON. If omitted, latest intake/analysis/*.analysis.json is used.",
    )
    parser.add_argument(
        "--reference-song-path",
        help="Optional path to a reference song directory containing render.yaml/meta.yaml.",
    )
    parser.add_argument(
        "--song-intent-path",
        help="Optional path to song_intent YAML/JSON for intent-aware comparison.",
    )
    return parser.parse_args()


def _pick_latest_analysis_json() -> Path:
    candidates = sorted(intake_analysis_dir().glob("*.analysis.json"), key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"No analysis JSON files found under: {intake_analysis_dir()}")
    return candidates[-1]


def _infer_reference_song_dir(analysis_path: Path) -> Path | None:
    stem = analysis_path.name
    if stem.endswith(".analysis.json"):
        stem = stem[: -len(".analysis.json")]
    if stem.startswith("tmp_"):
        maybe_ref = stem.split("_")
        if len(maybe_ref) >= 4:
            song_ref = "_".join(maybe_ref[1:-2])
            candidate = reference_song_dir(song_ref)
            if candidate.exists():
                return candidate
    return None


def main() -> int:
    args = parse_args()
    analysis_path = Path(args.analysis_json_path).resolve() if args.analysis_json_path else _pick_latest_analysis_json()

    explicit_reference = Path(args.reference_song_path).resolve() if args.reference_song_path else None
    inferred_reference = explicit_reference or _infer_reference_song_dir(analysis_path)
    song_intent_path = Path(args.song_intent_path).resolve() if args.song_intent_path else None

    try:
        result = run_reconstruction(
            analysis_json_path=analysis_path,
            reconstructed_root=intake_reconstructed_dir(),
            reference_song_dir=inferred_reference,
            song_intent_path=song_intent_path,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"[reconstruct] error: {exc}")
        return 1

    print(f"[reconstruct] input: {analysis_path}")
    print(f"[reconstruct] temporary_id: {result.temporary_id}")
    print(f"[reconstruct] comparison_mode: {result.comparison_mode}")
    if inferred_reference is not None:
        print(f"[reconstruct] reference: {inferred_reference}")
    if song_intent_path is not None:
        print(f"[reconstruct] song_intent: {song_intent_path}")
    print(f"[reconstruct] wrote: {result.render_path}")
    print(f"[reconstruct] wrote: {result.meta_path}")
    print(f"[reconstruct] wrote: {result.comparison_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
