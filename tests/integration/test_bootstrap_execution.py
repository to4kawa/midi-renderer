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
                "format: bootstrap",
                "transport:",
                "  bpm: 120",
                "  ppq: 480",
                "  time_signature: '4/4'",
                "tracks:",
                "  - id: piano",
                "    name: Piano",
                "    channel: 0",
                "    program: 0",
                "notes:",
                "  - track: piano",
                "    pitch: 60",
                "    start: '1:1:0'",
                "    duration: '0:1:0'",
                "    velocity: 96",
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "out.mid"

    cmd = [sys.executable, "scripts/run_render.py", str(spec), "--output", str(output)]
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)

    assert completed.returncode == 0, completed.stderr
    assert output.exists()
    assert output.read_bytes().startswith(b"MThd")
    assert "[bootstrap-render] wrote:" in completed.stdout


def test_bootstrap_canonical_song_path_runs(tmp_path: Path) -> None:
    output = tmp_path / "render_result.mid"

    cmd = [
        sys.executable,
        "scripts/run_render.py",
        "songs/neko_funjatta_test_piano_120/render.yaml",
        "--output",
        str(output),
    ]
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)

    assert completed.returncode == 0, completed.stderr
    assert output.exists()
    assert output.read_bytes().startswith(b"MThd")
    assert "[bootstrap-render] wrote:" in completed.stdout
