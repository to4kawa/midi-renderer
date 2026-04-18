from __future__ import annotations

import json
from pathlib import Path

from midi_renderer.renderer import RenderResult


def write_placeholder_output(result: RenderResult, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "song_ref": result.song_ref,
        "event_count": result.event_count,
        "payload": result.payload,
        "artifact_type": "bootstrap-placeholder",
    }

    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output
