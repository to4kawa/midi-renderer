import subprocess
import sys
from pathlib import Path


def test_bootstrap_entrypoint_runs(tmp_path: Path) -> None:
    spec = tmp_path / "render.yaml"
    spec.write_text(
        "\n".join(
            [
                "schema_version: '0.1'",
                "song_ref: test-song",
                "format:",
                "  type: midi",
                "transport:",
                "  bpm: 120",
                "  ppq: 480",
                "  time_signature: '4/4'",
                "tracks: []",
                "notes: []",
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "out.json"

    cmd = [sys.executable, "scripts/run_render.py", str(spec), "--output", str(output)]
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)

    assert completed.returncode == 0, completed.stderr
    assert output.exists()
    assert "[bootstrap-render] wrote:" in completed.stdout
