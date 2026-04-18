#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from midi_renderer.loader import load_render_spec
from midi_renderer.renderer import render
from midi_renderer.validator import ValidationError, validate_render_spec
from midi_renderer.writer import write_placeholder_output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run bootstrap render pipeline")
    parser.add_argument("render_spec", help="Path to render.yaml")
    parser.add_argument(
        "--output",
        default="out/render_result.json",
        help="Path to placeholder output artifact",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spec_path = Path(args.render_spec)

    try:
        spec = load_render_spec(spec_path)
        validate_render_spec(spec)
        result = render(spec)
        output = write_placeholder_output(result, args.output)
    except (OSError, ValueError, ValidationError) as exc:
        print(f"[bootstrap-render] error: {exc}")
        return 1

    print(f"[bootstrap-render] wrote: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
