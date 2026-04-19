from pathlib import Path

from midi_renderer.loader import load_render_spec


def test_load_render_spec_reads_yaml(tmp_path: Path) -> None:
    yaml_path = tmp_path / "render.yaml"
    yaml_path.write_text("schema_version: 'render.v0.1'\n", encoding="utf-8")

    result = load_render_spec(yaml_path)

    assert result["schema_version"] == "render.v0.1"
