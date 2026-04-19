#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from midi_renderer.analysis.midi_to_json import write_analysis_json
from midi_renderer.common.paths import intake_analysis_dir, intake_midi_dir, repo_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert one MIDI file to provisional analysis JSON")
    parser.add_argument(
        "midi_path",
        nargs="?",
        help="Optional path to a MIDI file. If omitted, one file is picked from intake/midi/.",
    )
    return parser.parse_args()


def _pick_one_midi() -> Path:
    candidates = sorted(intake_midi_dir().glob("*.mid")) + sorted(intake_midi_dir().glob("*.midi"))
    if not candidates:
        raise FileNotFoundError(f"No MIDI files found under: {intake_midi_dir()}")
    return candidates[0]


def main() -> int:
    args = parse_args()
    midi_path = Path(args.midi_path).resolve() if args.midi_path else _pick_one_midi()

    try:
        result = write_analysis_json(
            midi_path=midi_path,
            output_dir=intake_analysis_dir(),
            repository_root=repo_root(),
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"[midi-to-json] error: {exc}")
        return 1

    print(f"[midi-to-json] input: {midi_path}")
    print(f"[midi-to-json] temporary_id: {result.temporary_id}")
    print(f"[midi-to-json] analysis_id: {result.analysis_id}")
    print(f"[midi-to-json] wrote: {result.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
