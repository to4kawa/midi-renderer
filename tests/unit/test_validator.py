import pytest

from midi_renderer.validator import ValidationError, validate_render_spec


def test_validator_rejects_missing_required_fields() -> None:
    spec = {"schema_version": "render.v0.1"}

    with pytest.raises(ValidationError):
        validate_render_spec(spec)


def test_validator_accepts_minimal_valid_shape() -> None:
    spec = {
        "schema_version": "render.v0.1",
        "song_ref": "placeholder",
        "format": "bootstrap",
        "transport": {"bpm": 120, "ppq": 480, "time_signature": "4/4"},
        "tracks": [],
        "notes": [],
    }

    validate_render_spec(spec)
