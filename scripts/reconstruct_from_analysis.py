#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from midi_renderer.common.paths import (
    intake_analysis_dir,
    intake_reconstructed_dir,
    reference_neko_song_dir,
)
from midi_renderer.reconstruct.run_reconstruction import run_reconstruction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reconstruct trial render/meta from analysis JSON")
    parser.add_argument(
        "analysis_json_path",
        nargs="?",
        help="Path to analysis.v0.1 JSON. If omitted, latest intake/analysis/*.analysis.json is used.",
    )
    return parser.parse_args()


def _pick_latest_analysis_json() -> Path:
    candidates = sorted(intake_analysis_dir().glob("*.analysis.json"), key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"No analysis JSON files found under: {intake_analysis_dir()}")
    return candidates[-1]


def main() -> int:
    args = parse_args()
    analysis_path = Path(args.analysis_json_path).resolve() if args.analysis_json_path else _pick_latest_analysis_json()

    try:
        result = run_reconstruction(
            analysis_json_path=analysis_path,
            reconstructed_root=intake_reconstructed_dir(),
            reference_song_dir=reference_neko_song_dir(),
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"[reconstruct] error: {exc}")
        return 1

    print(f"[reconstruct] input: {analysis_path}")
    print(f"[reconstruct] temporary_id: {result.temporary_id}")
    print(f"[reconstruct] wrote: {result.render_path}")
    print(f"[reconstruct] wrote: {result.meta_path}")
    print(f"[reconstruct] wrote: {result.comparison_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
